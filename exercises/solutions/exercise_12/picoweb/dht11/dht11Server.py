import picoweb
import time
from machine import Pin
# import the DHT11 class
from dht import DHT11
import wifi_connect

# create a DHT11 object
_DHT11_PIN = 22
dht11 = DHT11(Pin(_DHT11_PIN))

print ("Connecting to the network")
wifi_connect.connect()
ipaddr=wifi_connect.getIPAddress()

app = picoweb.WebApp(None)

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

@app.route("/")
@app.route("/temp")
def html(req, resp):
    # take a measurement
    dht11.measure()
    t = dht11.temperature()
    h = dht11.humidity()
    print("Temperature: ",t,"°C, Humidity: ",h,"%")
    tm = time.localtime(time.time())
    timeStamp = '{0:02d} {1} {2:04d} {3:02d}:{4:02d}:{5:02d}'.format(tm[2],monthTable[tm[1]],tm[0],tm[3],tm[4],tm[5])
    sensor={"tmpr":t,"hmdty":h,"timeStamp":timeStamp}
    msg = (b'{0:3.1f} {1:3.1f}'.format(t,h))
    print(msg)
    yield from picoweb.start_response(resp, content_type = "text/html; charset=utf-8")
    yield from app.render_template(resp, "sensor.tpl", (sensor,))
    
app.run(debug=True, host =ipaddr,port=80)
