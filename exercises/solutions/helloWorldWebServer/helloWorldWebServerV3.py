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
    yield from app.sendfile(resp, "html/helloWorldV2.html.gz",content_type = "text/html; charset=utf-8",
                            headers=b"Content-Encoding: gzip\r\n") 

import ulogging as logging
logging.basicConfig(level=logging.INFO)

app.run(debug=2, host = ipaddr,port=80)
