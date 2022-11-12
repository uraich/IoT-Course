# The simplest possible WEB server printing "Hello World!"
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich April 2020
# This program is released under GPL

from microdot.microdot_asyncio import Microdot, send_file
from wifi_connect import connect, getIPAddress

print ("Connecting to the network")
connect()

app = Microdot()

@app.route("/")
def index(req):
     return send_file("html/helloWorld.html")
      
print("Starting the Hello World WEB server on http://" + getIPAddress() + " port 80")
app.run(debug=True, host = getIPAddress(), port=80)
