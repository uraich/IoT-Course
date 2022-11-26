#
# This is a picoweb example showing a Server Side Events (SSE) aka
# EventSource handling. Each connecting client gets its own events,
# independent from other connected clients.
#
import uasyncio
import picoweb
import network
from wifi_connect import *

# import the SHT3X class
from sht3x import SHT3X,SHT3XError
import sys

# create a SHT3X object
try:
    sht30 = SHT3X()
except SHT3XError as exception:
    if exception.error_code == SHT3XError.BUS_ERROR:
        print("SHT30 module not found on the I2C bus, please connect it")
        sys.exit(-1)
    else:
         raise exception
connect()
ipaddr=getIPAddress()

def index(req, resp):
    yield from picoweb.start_response(resp)
    htmlFile = open('/html/sensorEvt.html', 'r')
    for line in htmlFile:
        yield from resp.awrite(line)


def events(req, resp):
    print("Event source connected")
    yield from resp.awrite("HTTP/1.0 200 OK\r\n")
    yield from resp.awrite("Content-Type: text/event-stream\r\n")
    yield from resp.awrite("\r\n")
    i=0
    try:
        while True:
          tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
          timeStamp=dateString(cetTime())
          measurement="data: temperature={:2.1f},humidity={:2.1f},timeStamp={:s}\n\n".format(tempC,humi,timeStamp)
          yield from resp.awrite(measurement)
          yield from uasyncio.sleep(3)
          i += 1
    except OSError:
      print("Event source connection closed")
      yield from resp.aclose()


ROUTES = [
    ("/", index),
    ("/events", events),
]


import ulogging as logging
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

app = picoweb.WebApp("eventSource", ROUTES)
app.run(debug=True,host=ipaddr,port=80)
