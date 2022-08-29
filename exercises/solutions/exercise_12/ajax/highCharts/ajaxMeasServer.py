# ajaxMeasServer makes a measurement on the SHT30 when a, AJAX request comes
# in from the browser. It the constructs a message containing the measurement
# results and a timestamp. These data are then displayed in a table on the
# browser. The program needs the sensor.html file installed in the
# html directory of the ESP32
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich June 2020
# This program is released under GPL

import picoweb
import time
import network
import uasyncio as asyncio
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
       
print ("Connecting to the network")
connect()
ipaddr=getIPAddress()

print("Starting a simple javascript WEB server")

app = picoweb.WebApp("__main__")

@app.route("/")
@app.route("/index")
def index(req, resp):
  print(req)

  yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
  htmlFile = open('html/helloWorld.html', 'r')

  for line in htmlFile:
      yield from resp.awrite(line)

@app.route("/firstAjax")
def index(req, resp):
  print(req)

  yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
  htmlFile = open('html/firstAjax.html', 'r')

  for line in htmlFile:
      yield from resp.awrite(line)
      
@app.route("/sensor")
def index(req, resp):
  print(req)

  yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
  htmlFile = open('html/sensor.html', 'r')

  for line in htmlFile:
      yield from resp.awrite(line)
      
@app.route("/sensorTimer")
def index(req, resp):
  print(req)

  yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
  htmlFile = open('html/sensorTimer.html', 'r')

  for line in htmlFile:
      yield from resp.awrite(line)
      
@app.route("/sht30MeasAndPlot")
def index(req, resp):
  print(req)

  yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
  htmlFile = open('html/sht30MeasAndPlot.html', 'r')

  for line in htmlFile:
      yield from resp.awrite(line)
      
@app.route("/dummySensor")
def index(req, resp):
  print(req)

  yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
  htmlFile = open('html/dummySensor.html', 'r')

  for line in htmlFile:
      yield from resp.awrite(line)     
@app.route("/ajax_info.txt")
def index(req, resp):
  print(req)

  yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
  htmlFile = open('html/ajax_info.txt', 'r')

  for line in htmlFile:
      yield from resp.awrite(line)
      
@app.route("/measurement")

def index(req, resp):
  print(req)

  yield from picoweb.start_response(resp, content_type = "text/html"; charset=utf-8)
  tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
  timeStamp=dateString(cetTime())
  measurement="temperature={:2.1f},humidity={:2.1f},timeStamp={:s}".format(tempC,humi,timeStamp)
  print(measurement)
  yield from resp.awrite(measurement)

app.run(debug=2, host = ipaddr,port=80)
