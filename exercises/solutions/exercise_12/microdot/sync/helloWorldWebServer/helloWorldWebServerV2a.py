# The simplest possible WEB server printing "Hello World!"
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich April 2020
# This program is released under GPL

from microdot.microdot import Microdot, Response
from wifi_connect import connect, getIPAddress

print ("Connecting to the network")
connect()

app = Microdot()

@app.route("/")
def index(req):
     htmlFile = open('html/helloWorld.html', 'r')
     body = ""
     for line in htmlFile:
          body += line
     response = Response(body,headers={"Content-Type" : "text/html"})
     return response

print("Starting web server on  http://" + getIPAddress() + " port 80")      
app.run(debug=True, host = getIPAddress(), port=80)
