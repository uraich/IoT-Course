# ledAndMeasServer makes a measurement on the SHT30 when a, AJAX request comes
# in from the browser. It constructs a message containing the measurement
# results and a timestamp. These data are then displayed in a table on the
# browser. It also allows to control the user LED
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich June 2020
# This program is released under GPL

from microdot.microdot_asyncio import Microdot, send_file
from wifi_connect import connect, getIPAddress, dateString, cetTime
from machine import Pin
import os

osVersion=os.uname()
# if there is 'spiram' in the machine name then we are on the T7 V1.4
if osVersion.machine.find('spiram') == -1:
    _LED_PIN = 2
else:
    _LED_PIN = 19
led = Pin(_LED_PIN,Pin.OUT)
    
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
       
print ("Connecting to the network")
connect()

print("Starting a simple javascript WEB server")

app = Microdot()

@app.route("/")
@app.route("/index")
def index(req):
    print(req)
    return send_file("html/ledAndMeas.html",content_type="text/html; charset=utf-8")

@app.route("/measurement")
def index(req):
    print(req)

    tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
    timeStamp=dateString(cetTime())
    measurement="temperature={:2.1f},humidity={:2.1f},timeStamp={:s}".format(tempC,humi,timeStamp)
    print(measurement)
    return measurement
  
@app.route('/static/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path)

@app.route("/ledOn")
def index(req):
  led.on() 
  print("led on")
  return "led=on"
  
@app.route("/ledOff")
def index(req):
  led.off()   
  print("led off")
  return "led=off"

print("Running the ajax server on http://" + getIPAddress())  
app.run(debug=2, host = getIPAddress(), port=80)
