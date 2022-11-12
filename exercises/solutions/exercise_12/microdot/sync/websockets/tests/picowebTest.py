# Picoweb web pico-framework for Pycopy, https://github.com/pfalcon/pycopy
# Copyright (c) 2014-2020 Paul Sokolovsky
# SPDX-License-Identifier: MIT
import sys
import gc
import micropython
import utime
import uio
import ure as re
import uerrno
import uasyncio as asyncio
import pkg_resources
import ulogging as logging
from hashlib import sha1
from binascii import b2a_base64
import websocket
from wifi_connect import *
from machine      import Timer,Pin
# import the SHT3X class
from sht3x        import SHT3X,SHT3XError
import sys

tm = Timer(0)  # Instatiate hardware timer
led = Pin(2,Pin.OUT)

# create a SHT3X object
try:
    sht30 = SHT3X()
except SHT3XError as exception:
    if exception.error_code == SHT3XError.BUS_ERROR:
        print("SHT30 module not found on the I2C bus, please connect it")
        sys.exit(-1)
    else:
         raise exception
    

SEND_BUFSZ = 128

def unquote_plus(s):
    # TODO: optimize
    s = s.replace("+", " ")
    arr = s.split("%")
    arr2 = [chr(int(x[:2], 16)) + x[2:] for x in arr[1:]]
    return arr[0] + "".join(arr2)

def parse_qs(s):
    res = {}
    if s:
        pairs = s.split("&")
        for p in pairs:
            vals = [unquote_plus(x) for x in p.split("=", 1)]
            if len(vals) == 1:
                vals.append(True)
            old = res.get(vals[0])
            if old is not None:
                if not isinstance(old, list):
                    old = [old]
                    res[vals[0]] = old
                old.append(vals[1])
            else:
                res[vals[0]] = vals[1]
    return res

def get_mime_type(fname):
    # Provide minimal detection of important file
    # types to keep browsers happy
    if fname.endswith(".html"):
        return "text/html"
    if fname.endswith(".css"):
        return "text/css"
    if fname.endswith(".png") or fname.endswith(".jpg"):
        return "image"
    return "text/plain"

def sendstream(writer, f):
    buf = bytearray(SEND_BUFSZ)
    while True:
        l = f.readinto(buf)
        if not l:
            break
        yield from writer.awrite(buf, 0, l)


def jsonify(writer, dict):
    import ujson
    yield from start_response(writer, "application/json")
    yield from writer.awrite(ujson.dumps(dict))

def start_response(writer, content_type="text/html; charset=utf-8", status="200", headers=None):
    yield from writer.awrite("HTTP/1.0 %s NA\r\n" % status)
    yield from writer.awrite("Content-Type: ")
    yield from writer.awrite(content_type)
    if not headers:
        yield from writer.awrite("\r\n\r\n")
        return
    print("Headers:")
    yield from writer.awrite("\r\n")
    if isinstance(headers, bytes) or isinstance(headers, str):
        yield from writer.awrite(headers)
    else:
        for k, v in headers.items():
            yield from writer.awrite(k)
            yield from writer.awrite(": ")
            yield from writer.awrite(v)
            yield from writer.awrite("\r\n")
    yield from writer.awrite("\r\n")

def http_error(writer, status):
    yield from start_response(writer, status=status)
    yield from writer.awrite(status)


class HTTPRequest:

    def __init__(self):
        pass

    def read_form_data(self):
        size = int(self.headers[b"Content-Length"])
        data = yield from self.reader.readexactly(size)
        form = parse_qs(data.decode())
        self.form = form

    def parse_qs(self):
        form = parse_qs(self.qs)
        self.form = form


class WebApp:

    def __init__(self, pkg, routes=None, serve_static=True):
        if routes:
            self.url_map = routes
        else:
            self.url_map = []
        if pkg and pkg != "__main__":
            self.pkg = pkg.split(".", 1)[0]
        else:
            self.pkg = None
        if serve_static:
            self.url_map.append((re.compile("^/(static/.+)"), self.handle_static))
        self.mounts = []
        self.inited = False
        # Instantiated lazily
        self.template_loader = None
        self.headers_mode = "parse"

    def getReader(self):
        return self.reader

    def getWriter(self):
        return self.writer
    
    def parse_headers(self, reader):
        headers = {}
        while True:
            l = yield from reader.readline()
            print("In parse headers: ",l)
            if l == b"\r\n":
                break
            k, v = l.split(b":", 1)
            headers[k] = v.strip()
        print("Headers:")
        print(headers)
        return headers
            
    def _handle(self, reader, writer):
        self.reader=reader
        self.writer=writer
        
        if self.debug > 1:
            print("memory sizes: ",micropython.mem_info())
        close = True
        req = None
        try:
            request_line = yield from reader.readline()
            print("request line: ",request_line)
            if request_line == b"":
                if self.debug >= 0:
                    self.log.error("%s: EOF on request start" % reader)
                yield from writer.aclose()
                return
            req = HTTPRequest()
            # TODO: bytes vs str
            request_line = request_line.decode()
            method, path, proto = request_line.split()
            if self.debug >= 0:
                self.log.info('%.3f %s %s "%s %s"' % (utime.time(), req, writer, method, path))
            path = path.split("?", 1)
            qs = ""
            if len(path) > 1:
                qs = path[1]
            path = path[0]

            print("================")
            print(req, writer)
            print(req, (method, path, qs, proto))

            # Find which mounted subapp (if any) should handle this request
            app = self
            while True:
                found = False
                for subapp in app.mounts:
                    root = subapp.url
                    #print(path, "vs", root)
                    if path[:len(root)] == root:
                        app = subapp
                        found = True
                        path = path[len(root):]
                        if not path.startswith("/"):
                            path = "/" + path
                        break
                if not found:
                    break

            # We initialize apps on demand, when they really get requests
            if not app.inited:
                app.init()

            # Find handler to serve this request in app's url_map
            found = False
            for e in app.url_map:
                pattern = e[0]
                handler = e[1]
                print(pattern,handler)
                extra = {}
                if len(e) > 2:
                    extra = e[2]

                if path == pattern:
                    found = True
                    break
                elif not isinstance(pattern, str):
                    # Anything which is non-string assumed to be a ducktype
                    # pattern matcher, whose .match() method is called. (Note:
                    # Django uses .search() instead, but .match() is more
                    # efficient and we're not exactly compatible with Django
                    # URL matching anyway.)
                    m = pattern.match(path)
                    if m:
                        req.url_match = m
                        found = True
                        break

            if not found:
                print("not found")
                headers_mode = "skip"
            else:
                headers_mode = extra.get("headers", self.headers_mode)

            if headers_mode == "skip":
                while True:
                    l = yield from reader.readline()
                    print("skip: line read: ",l)
                    if l == b"\r\n":
                        break
            elif headers_mode == "parse":
                print("parse")
                req.headers = yield from self.parse_headers(reader)
            else:
                assert headers_mode == "leave"

            if found:
                req.method = method
                req.path = path
                req.qs = qs
                req.reader = reader
                close = yield from handler(req, writer)
            else:
                yield from start_response(writer, status="404")
                yield from writer.awrite("404\r\n")
            #print(req, "After response write")
        except Exception as e:
            if self.debug >= 0:
                self.log.exc(e, "%.3f %s %s %r" % (utime.time(), req, writer, e))
            yield from self.handle_exc(req, writer, e)

        if close is not False:
            yield from writer.aclose()
        if __debug__ and self.debug > 1:
            self.log.debug("%.3f %s Finished processing request", utime.time(), req)

    def handle_exc(self, req, resp, e):
        # Can be overriden by subclasses. req may be not (fully) initialized.
        # resp may already have (partial) content written.
        # NOTE: It's your responsibility to not throw exceptions out of
        # handle_exc(). If exception is thrown, it will be propagated, and
        # your webapp will terminate.
        # This method is a coroutine.
        if 0: yield

    def mount(self, url, app):
        "Mount a sub-app at the url of current app."
        # Inspired by Bottle. It might seem that dispatching to
        # subapps would rather be handled by normal routes, but
        # arguably, that's less efficient. Taking into account
        # that paradigmatically there's difference between handing
        # an action and delegating responisibilities to another
        # app, Bottle's way was followed.
        app.url = url
        self.mounts.append(app)
        # TODO: Consider instead to do better subapp prefix matching
        # in _handle() above.
        self.mounts.sort(key=lambda app: len(app.url), reverse=True)

    def route(self, url, **kwargs):
        def _route(f):
            self.url_map.append((url, f, kwargs))
            return f
        return _route

    def add_url_rule(self, url, func, **kwargs):
        # Note: this method skips Flask's "endpoint" argument,
        # because it's alleged bloat.
        self.url_map.append((url, func, kwargs))

    def _load_template(self, tmpl_name):
        if self.template_loader is None:
            import utemplate.source
            self.template_loader = utemplate.source.Loader(self.pkg, "templates")
        return self.template_loader.load(tmpl_name)

    def render_template(self, writer, tmpl_name, args=()):
        tmpl = self._load_template(tmpl_name)
        for s in tmpl(*args):
            yield from writer.awritestr(s)

    def render_str(self, tmpl_name, args=()):
        #TODO: bloat
        tmpl = self._load_template(tmpl_name)
        return ''.join(tmpl(*args))

    def sendfile(self, writer, fname, content_type=None, headers=None):
        if not content_type:
            content_type = get_mime_type(fname)
        try:
            with pkg_resources.resource_stream(self.pkg, fname) as f:
                yield from start_response(writer, content_type, "200", headers)
                yield from sendstream(writer, f)
        except OSError as e:
            if e.args[0] == uerrno.ENOENT:
                yield from http_error(writer, "404")
            else:
                raise

    def handle_static(self, req, resp):
        path = req.url_match.group(1)
        print(path)
        if ".." in path:
            yield from http_error(resp, "403")
            return
        yield from self.sendfile(resp, path)

    def init(self):
        """Initialize a web application. This is for overriding by subclasses.
        This is good place to connect to/initialize a database, for example."""
        self.inited = True

    def serve(self, loop, host, port):
        # Actually serve client connections. Subclasses may override this
        # to e.g. catch and handle exceptions when dealing with server socket
        # (which are otherwise unhandled and will terminate a Picoweb app).
        # Note: name and signature of this method may change.
        loop.create_task(asyncio.start_server(self._handle, host, port))
        loop.run_forever()

    def run(self, host="127.0.0.1", port=8081, debug=False, lazy_init=False, log=None):
        if log is None and debug >= 0:
            import ulogging
            log = ulogging.getLogger("picoweb")
            if debug > 0:
                log.setLevel(ulogging.DEBUG)
        self.log = log
        gc.collect()
        self.debug = int(debug)
        self.init()
        if not lazy_init:
            for app in self.mounts:
                app.init()
        loop = asyncio.get_event_loop()
        if debug > 0:
            print("* Running on http://%s:%s/" % (host, port))
        self.serve(loop, host, port)
        loop.close()

TEXT = 0x01
BINARY = 0x02
CLOSE = 0x08

def make_respkey(webkey):
    try:
        webkey += b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        respkey = sha1(webkey).digest()
        respkey = b2a_base64(respkey).decode().strip()
        print('respkey: ',respkey)
        return respkey
    except Exception as e:
        print("Error in handshake: ",e)
        return None
    
class WSWriter:

    def __init__(self, reader, writer):
        # Reader is passed for symmetry with WSReader() and ignored.
        self.writer = writer
    async def awrite (self, data):
        print("Sending: ",data)
        length = len(data)
        ret = None
        if length <= 125:
            ret = bytearray([129, length])

        for byte in data.encode("utf-8"):
            ret.append(byte)
        print("ret: ",ret)
        yield from self.writer.awrite(ret)
        print("sent: ",ret)

class WSReader:
    def __init__(self,reader,writer):    
        self.reader=reader
        self.writer=writer
        
    async def connect(self,req):
        webkey = None
        print("check if Sec-WebSocket-Key exists in header")
        if b'Sec-WebSocket-Key' in req.headers:
            print('websocket connect request seen')
            webkey = req.headers[b'Sec-WebSocket-Key']
        else:
            raise ValueError("Not a websocker request")

        print("webkey: ",webkey)
        respkey = make_respkey(webkey)
        print("response key created")
        print(b"""\
HTTP/1.1 101 Switching Protocols\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Accept: """)
        
        await self.writer.awrite(b"""\
HTTP/1.1 101 Switching Protocols\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Accept: """)
        
        await self.writer.awrite(respkey)
        print(respkey)
        await self.writer.awrite("\r\n\r\n")
        print("Finished webrepl handshake")
        ws = websocket.websocket(self.reader.s)
        self.ws_reader = asyncio.StreamReader(self.reader.s, ws)

    async def read(self,length):
        data = await self.ws_reader.read(length)
        print("websocket frame: ",data)
        if not data: return data
        """
            Parse a WebSocket frame. If there is not a complete frame in the
            buffer, return without modifying the buffer.
        """
        payload_start = 2

        # try to pull first two bytes
        if len(data) < 3: return
        for i in range(len(data)):
            print(hex(data[i])," ",end="")
        print("")

        b=data[0]
        fin = b & 0x80      # 1st bit
        print("fin: ",fin)
        # next 3 bits reserved    
        opcode = b & 0x0f   # low 4 bits
        print(opcode)
        
        b2=data[1]   
        mask = b2 & 0x80      # high bit of the second byte
        if mask:
            print("mask bit is set")
        length = b2 & 0x7f    # low 7 bits of the second byte

        # check that enough bytes remain
        if len(data) < payload_start + 4:
            return
        elif length == 126:
            length, = struct.unpack(">H", data[2:4])
            payload_start += 2
        elif length == 127:
            length, = struct.unpack(">I", data[2:6])
            payload_start += 4

        if mask:
#        mask_bytes = [ord(b) for b in data[payload_start:payload_start + 4]]
            mask_bytes = [b for b in data[payload_start:payload_start + 4]]
            print("mask bytes: ",mask_bytes)
            payload_start += 4
            
        # is there a complete frame in the buffer?
        if len(data) < payload_start + length:
            return

        # remove leading bytes, decode if necessary, dispatch
        payload = data[payload_start:payload_start + length]
        print("payload: ",payload)
        data = data[payload_start + length:]

        # use xor and mask bytes to unmask data
        if mask:
#        unmasked = [mask_bytes[i % 4] ^ ord(b) for b, i in zip(payload, range(len(payload)))]
            unmasked = [mask_bytes[i % 4] ^ b for b, i in zip(payload, range(len(payload)))]
            for i in range(len(unmasked)):
                print("unmasked: ",hex(unmasked[i]))

            payload = "".join([chr(c) for c in unmasked])

        if opcode == TEXT:
            print("payload string: ",payload)
            ret = payload
            #self.handler.dispatch(s)
        if opcode == BINARY:
            print("BINARY websockets are not yet implemented")
            #self.handler.dispatch(payload)
            assert(0)
        if opcode == CLOSE:
            print("Payload length: ",len(payload))
            for i in range(len(payload)):
                print(hex(ord(payload[i]))," ",end="")
            print("")
            return None

        print(ret)
        return ret
    
def cb_timer(timer, writer):
    tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
    timeStamp=dateString(cetTime())
    content="temperature={:2.1f},humidity={:2.1f},timeStamp={:s}".format(tempC,humi,timeStamp)
    print(content)
    writer.awrite(content)        

app = WebApp("__main__")

@app.route("/")
@app.route("/index.html")
def index(req, resp):
     print("headers in /",req.headers)
     try:
          print("Request in index: ",req)
          reader = WSReader(req.reader,resp)
          await reader.connect(req)
          writer = WSWriter(req.reader, resp)
          print("websocket connection established")
          cb = lambda timer: cb_timer(timer, writer)  # Use lambda to inject writer
          tm.init(period=3000, callback=cb)           # Init and start timer to poll temperature sensor
          
          while 1:
               l = yield from reader.read(256)
               print("Read line: ",l)
                

     except ValueError:
          # Not a websocket connection, serve webpage
          yield from app.sendfile(resp, "html/helloWorld.html",content_type = "text/html; charset=utf-8")
          return

@app.route("/sensor.html")
def index(req, resp):
     htmlFile = open('html/sensor.html', 'r')
     for line in htmlFile:
          yield from resp.awrite(line)
            
connect()
ipaddr=getIPAddress()
app.run(debug=2, host = ipaddr,port=80)
