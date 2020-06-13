# This module is a simplistic telnet server for the ESP processors
# It was built as a combination of webrepl and
# https://github.com/cpopp/MicroTelnetServer/blob/master/utelnet/utelnetserver.py
# With some slight modification (included uos.dupterm_notify) it now works on
# micropython-1.2
# 
import socket
import uos
import network
import errno
from uio import IOBase
from wifi_connect import *

listen_s = None
client_s = None

# Provide necessary functions for dupterm and replace telnet control characters that come in.
class TelnetWrapper(IOBase):
    def __init__(self, socket):

        self.socket = socket
        self.discard_count = 0
        
    def readinto(self, b):
        readbytes = 0

        for i in range(len(b)):
            try:
                byte = 0
                # discard telnet control characters and
                # null bytes 
                while(byte == 0):
                    byte = self.socket.recv(1)[0]
                    if byte == 0xFF:
                        self.discard_count = 2
                        byte = 0
                    elif self.discard_count > 0:
                        self.discard_count -= 1
                        byte = 0
                    
                b[i] = byte
                
                readbytes += 1
            except (IndexError, OSError) as e:
                if type(e) == IndexError or len(e.args) > 0 and e.args[0] == errno.EAGAIN:
                    if readbytes == 0:
                        return None
                    else:
                        return readbytes
                else:
                    raise
        return readbytes
    
    def write(self, data):
        import errno
        # we need to write all the data but it's a non-blocking socket
        # so loop until it's all written eating EAGAIN exceptions
        while len(data) > 0:
            try:
                written_bytes = self.socket.write(data)
                data = data[written_bytes:]
            except OSError as e:
                if len(e.args) > 0 and e.args[0] == errno.EAGAIN:
                    # can't write yet, try again
                    pass
                if len(e.args) > 0 and e.args[0] == errno.ECONNRESET:
                    uos.dupterm(None)
                    print("Connection was reset\n")
                    break
                else:
                    # something else...propagate the exception
                    raise
    
    def close(self):
        self.socket.close()

def setup_conn(port, accept_handler):
    global listen_s
    listen_s = socket.socket()
    listen_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    ai = socket.getaddrinfo("0.0.0.0", port)
    addr = ai[0][4]

    listen_s.bind(addr)
    listen_s.listen(1)
    if accept_handler:
        listen_s.setsockopt(socket.SOL_SOCKET, 20, accept_handler)
    for i in (network.AP_IF, network.STA_IF):
        iface = network.WLAN(i)
        if iface.active():
            print("telnet server started on: %s:%d" % (iface.ifconfig()[0], port))
    return listen_s


def accept_conn(listen_sock):
    global client_s
    cl, remote_addr = listen_sock.accept()
    prev = uos.dupterm(None)
    uos.dupterm(prev)
    if prev:
        print("\nConcurrent telnet connection from", remote_addr, "rejected")
        cl.close()
        return
    print("\ntelnet connection from:", remote_addr)
    client_s = cl
    cl.setblocking(False)
    
    # notify REPL on socket incoming data (ESP32/ESP8266-only)
    if hasattr(uos, "dupterm_notify"):
        cl.setsockopt(socket.SOL_SOCKET, 20, uos.dupterm_notify)
    uos.dupterm(TelnetWrapper(cl))

def stop():
    global listen_s, client_s
    uos.dupterm(None)
    if client_s:
        client_s.close()
    if listen_s:
        listen_s.close()


def start(port=23):
    stop()
    setup_conn(port, accept_conn)
    print("Started telnet server")

