# ajaxMeasServer makes a measurement on the SHT30 when a, AJAX request comes
# in from the browser. It constructs a message containing the measurement
# results and a timestamp. These data are then displayed in a table on the
# browser. The program needs the sensor.html file installed in the
# html directory of the ESP32
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich June 2020
# This program is released under GPL

from microdot.microdot import Microdot, send_file
from wifi_connect import connect, getIPAddress, dateString, cetTime

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


app = Microdot()

@app.route("/")
@app.route("/index")
def index(req):
    print(req)
    return send_file("html/helloWorld.html",content_type="text/html; charset=utf-8")

@app.route("/firstAjax")
def index(req):
    print(req)
    return send_file("html/firstAjax.html",content_type="text/html; charset=utf-8")
      
@app.route("/sensor")
def index(req):
    print(req)
    return send_file("html/sensor.html",content_type="text/html; charset=utf-8")
      
@app.route("/sensorTimer")
def index(req):
    print(req)
    return send_file("html/sensorTimer.html",content_type="text/html; charset=utf-8")
      
@app.route("/ajax_info.txt")
def index(req):
    print(req)
    return send_file("html/ajax_info.txt")

    # yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
    # htmlFile = open('html/ajax_info.txt', 'r')

    # for line in htmlFile:
    #     yield from resp.awrite(line)
      
@app.route("/measurement")
def index(req):
    print(req)

    tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
    timeStamp=dateString(cetTime())
    measurement="temperature={:2.1f},humidity={:2.1f},timeStamp={:s}".format(tempC,humi,timeStamp)
    print(measurement)
    return measurement
  
@app.route("/dummyMeas")
def index(req):
    print(req)

    measurement="temperature=23.4°C,humidity=64%,timestamp=31.May 2020 14:08:00"
    print(measurement)
    return measurement
  
print("Starting a simple javascript WEB server on http://" + getIPAddress())
app.run(debug=2, host = getIPAddress(), port=80)
