# ajaxMeasServer makes a measurement on the SHT30 when a, AJAX request comes
# in from the browser. It the constructs a message containing the measurement
# results and a timestamp. These data are then displayed in a table on the
# browser. The program needs the sensor.html file installed in the
# html directory of the ESP32
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich June 2020
# This program is released under GPL

from microdot.microdot import Microdot, send_file
import time
import network
import uasyncio as asyncio
from wifi_connect import connect, getIPAddress
from machine import Pin
import os
osVersion=os.uname()
# if there is 'spiram' in the machine name then we are on the T7 V1.4
if osVersion.machine.find('spiram') == -1:
    _LED_PIN = 2
else:
    _LED_PIN = 19

print("LED is connected to GPIO ",_LED_PIN)
led=Pin(_LED_PIN,Pin.OUT) 
       
print ("Connecting to the network")
connect()

print("Starting a simple javascript WEB server")

app = Microdot()

@app.route("/")
@app.route("/dummyLED")
def index(req):
  print(req)
  return send_file('html/dummyLED.html',content_type = "text/html")

@app.route("/ledControl")
def index(req):
  print(req)
  return send_file('html/ledControl.html',content_type = "text/html")
      
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

@app.route('/static/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path)
  
app.run(debug=True, host = getIPAddress(), port=80)
