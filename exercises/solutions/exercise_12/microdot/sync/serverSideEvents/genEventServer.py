#
# This is a microdot example showing a Server Side Events (SSE) aka
# EventSource handling. Each connecting client gets its own events,
# independent from other connected clients.
#
# Copyright (c) U. Raich, Nov. 2022
# This program is part of the IoT course at the
# University of Cape Coast, Ghana
# It is released under the MIT license

from microdot.microdot import Microdot, Response, send_file
from wifi_connect import connect, getIPAddress, dateString, cetTime
from time import sleep

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
connect()
app = Microdot()

@app.route('/')
@app.route('/sht30MeasAndPlot')
def highCharts(req):
    return send_file('/html/sht30MeasAndPlot.html',content_type="text/html; charset=utf-8")

@app.route('/events')        
def events(req):
    app.send_evt_src_header()
    print("Event source connected")

    def sendEvents():
        try:
            while True:
                tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
                timeStamp=dateString(cetTime())
                measurement="data: temperature={:2.1f},humidity={:2.1f},timeStamp={:s}\n\n".format(tempC,humi,timeStamp)
                yield measurement
                sleep(3)
        except OSError:
            print("Event source connection closed")
            req.app.shutdown()

    return sendEvents()

import ulogging as logging
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

print("Please connect to http://"+getIPAddress())
app.run(debug=True,host=getIPAddress(),port=80)
