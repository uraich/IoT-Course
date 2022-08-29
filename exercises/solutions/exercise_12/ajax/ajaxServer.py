# ajaxServer serves the AJAX request for measurement data from the browser
# This version is a test version only and sends dummy temperature and
# humidity data and a dummy time stamp
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich April 2020
# This program is released under GPL

import picoweb
import time
import network
import uasyncio as asyncio
import wifi_connect

print ("Connecting to the network")
wifi_connect.connect()
ipaddr=wifi_connect.getIPAddress()

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

  yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
  measurement="temperature=23.4°C,humidity=64%,timestamp=31.May 2020 14:08:00"
  yield from resp.awrite(measurement)

app.run(debug=2, host = ipaddr,port=80)
