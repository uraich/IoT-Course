# The simplest possible WEB server printing "Hello World!"
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich April 2020
# This program is released under GPL

from microdot.microdot_syncio import Microdot, Response
from wifi_connect import connect, getIPAddress

print ("Connecting to the network")
connect()

print("Starting the Hello World WEB server")

app = Microdot()

@app.route("/")
def index(req):
    htmlFile = open('html/helloWorld.html.gz', 'rb')
    response = Response(body=htmlFile,
                        headers={"Content-Type" : "text/html; charset=utf-8",
                                 "Content-Encoding" : "gzip",
                                 "Vary": "Accept-Encoding"})
    return response
import ulogging as logging
logging.basicConfig(level=logging.INFO)

print("Please connect to http://" + getIPAddress())
app.run(debug=2, host = getIPAddress(), port=80)
