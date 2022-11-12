# sht30_async_websockets.py  makes a measurement on the SHT30 then the data
# are transferred to the browser via websockets
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich November 2022
# This program is released under the MIT license

from wifi_connect import connect, getIPAddress, cetTime, dateString
from microdot.microdot_asyncio import Microdot, send_file
from microdot.microdot_asyncio_websocket import with_websocket

# import the SHT3X class
from sht3x import SHT3X,SHT3XError
from machine import Pin
import os,sys
import uasyncio as asyncio 

# create LED object

osVersion=os.uname()
# if there is 'spiram' in the machine name then we are on the T7 V1.4
if osVersion.machine.find('spiram') == -1:
    _LED_PIN = 2
else:
    _LED_PIN = 19
led = Pin(_LED_PIN,Pin.OUT)
# switch user LED off
led.off()

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
app = Microdot()

@app.route('/')
def index(request):
    return send_file('/html/websockets.html')

@app.route('/static/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path)

@app.route('/meas')
@with_websocket
async def meas(request, ws):
    while True:
        tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,
                                           repeatability=SHT3X.REP_S_HIGH)
        timeStamp=dateString(cetTime())
        measurement="temperature={:2.1f},humidity={:2.1f},timeStamp={:s}".format(tempC,humi,timeStamp)
        print(measurement)
        await ws.send(measurement)
        yield from asyncio.sleep(3)

@app.route('led')
@with_websocket
async def led_control(request,ws):
    while True:
        cmd = await ws.receive()
        print(cmd)
        if cmd == "ledOn":
            led.on()
        elif cmd == "ledOff":
            led.off()
        else:
            print("Unknown command")
        await ws.send(cmd)
        
print("Please connect to http://" + getIPAddress())
app.run(debug=True, host=getIPAddress(), port=80)
