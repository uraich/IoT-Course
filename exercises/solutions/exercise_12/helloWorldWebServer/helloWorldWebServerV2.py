# The simplest possible WEB server printing "Hello World!"
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

print("Starting the Hello World WEB server")

app = picoweb.WebApp("__main__")

@app.route("/")
def index(req, resp):
     yield from app.sendfile(resp, "html/helloWorld.html",content_type = "text/html; charset=utf-8")
#  that's another way of doing it:
#  yield from picoweb.start_response(resp, content_type = "text/html")
#  htmlFile = open('html/helloWorld.html', 'r')

#  for line in htmlFile:
#      yield from resp.awrite(line)
      
app.run(debug=2, host = ipaddr,port=80)
