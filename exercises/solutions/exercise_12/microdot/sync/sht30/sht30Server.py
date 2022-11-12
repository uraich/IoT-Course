from microdot.microdot import Microdot, Response
from microdot.microdot_utemplate import render_template

import time
from machine import Pin
# import the SHT3X class
from sht3x import SHT3X,SHT3XError
from wifi_connect import connect, getIPAddress

print ("Connecting to the network")
connect()

app = Microdot()
Response.default_content_type = 'text/html'

monthTable ={ 1: 'January',
              2: 'February',
              3: 'March',
              4: 'April',
              5: 'May',
              6: 'June',
              7: 'July',
              8: 'August',
              9: 'September',
              10: 'October',
              11: 'November',
              12: 'December'}

# create a SHT3X object
try:
    sht30 = SHT3X()
except SHT3XError as exception:
    if exception.error_code == SHT3XError.BUS_ERROR:
        print("SHT30 module not found on the I2C bus, please connect it")
        sys.exit(-1)
    else:
         raise exception

@app.route("/")
@app.route("/temp")
def html(req):
    t,h = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
    print("Temperature: ",t,"°C, Humidity: ",h,"%")
    tm = time.localtime(time.time())
    timeStamp = '{0:02d} {1} {2:04d} {3:02d}:{4:02d}:{5:02d}'.format(tm[2],monthTable[tm[1]],tm[0],tm[3],tm[4],tm[5])
    sensor={"tmpr":t,"hmdty":h,"timeStamp":timeStamp}
    msg = (b'{0:3.1f} {1:3.1f}'.format(t,h))
    print(msg)
    # yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
    return render_template("sensor.tpl", sensor)
    
app.run(debug=True, host = getIPAddress(), port=80)
