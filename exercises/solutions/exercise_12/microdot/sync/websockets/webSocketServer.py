# In this version we try to integrate WEB sockets into the WEB server
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich April 2020
# This program is released under GPL

import picoweb
import time
import network
import uasyncio as asyncio
import ulogging as logging
from picoweb.websockets import WSReader, WSWriter
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
    
print ("Connecting to the network")
connect()
ipaddr=getIPAddress()

print("Starting the WEB socket server")

app = picoweb.WebApp("__main__")
global update
update = False
def cb_timer(timer, writer):
    global update
    #tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
    #timeStamp=dateString(cetTime())
    #content="temperature={:2.1f},humidity={:2.1f},timeStamp={:s}".format(tempC,humi,timeStamp)
    #print(content)
    #await writer.awrite(content)
    print("update")
    update = True


@app.route("/")
@app.route("/index.html")
def index(req, resp):
    global update
    try:
        print("Request in index: ",req)
        reader = WSReader(req.reader, resp)
        await reader.connect(req)
        writer = WSWriter(req.reader, resp)
        print("websocket connection established")
        print("Starting timer")
        cb = lambda timer: cb_timer(timer, writer)  # Use lambda to inject writer
        tm.init(period=3000, callback=cb)           # Init and start timer to poll temperature sensor

        while 1:
            #l = await reader.read(128)
            #print(l)
            if update:
                print("updating")
                tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
                timeStamp=dateString(cetTime())
                content="temperature={:2.1f},humidity={:2.1f},timeStamp={:s}".format(tempC,humi,timeStamp)
                print(content)
                await writer.awrite(content)
                update = False
                await asyncio.sleep_ms(10)
                
    except ValueError:
    # Not a websocket connection, serve webpage
        yield from app.sendfile(resp, "html/index.html",content_type = "text/html; charset=utf-8")
        return

@app.route("/sensor.html")
def index(req, resp):
     htmlFile = open('html/sensor.html', 'r')
     for line in htmlFile:
          yield from resp.awrite(line)
     
#  that's another way of doing it:
#  yield from picoweb.start_response(resp, content_type = "text/html")
#  htmlFile = open('html/helloWorld.html', 'r')

#  for line in htmlFile:
#      yield from resp.awrite(line)
      
app.run(debug=2, host = ipaddr,port=80)
