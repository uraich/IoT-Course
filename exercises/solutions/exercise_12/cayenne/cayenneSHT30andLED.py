#
# cayenneSHT30andLED.py
# Reads out the SHT30 temperature and humidity and sends the measurement
# to Cayenne. Has a button in addition to control the builtin LED
# copyright U. Raich
# This is a demo program for the workshop on IoT at the
# African Internet Summit 2019, Kampala
# Released under GPL
#
from machine import Pin
import cayenne.client
import sys,time
from sht3x import SHT3X,SHT3XError
import ulogging as logging

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "your mqtt user code"
MQTT_PASSWORD  = "your mqtt password"
MQTT_CLIENT_ID = "your mqtt client id 

sht30TempChannel = 0
sht30HumidityChannel = 2

global ledChannel
global builtinLed
ledChannel = 4
builtinLed = Pin(19,Pin.OUT)
# switch LED off
builtinLed.value(0) 

# callback routine to treat command messages from Cayenne
def on_message(message):
    global ledChannel
    msg = cayenne.client.CayenneMessage(message[0],message[1])
    if msg.channel == ledChannel:
        builtinLed.value(int(msg.value))
        if int(msg.value):
            print("Switching built-in led on");
        else:
            print("Switching built-in led off");
    return

# create SHT30 object
try:
    sht30 = SHT3X()
except SHT3XError as exception:
    if exception.error_code == SHT3XError.BUS_ERROR:
        print("SHT30 module not found on the I2C bus, please connect it")
        sys.exit(-1)
    else:
         raise exception   

sht30.softReset()

client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO)
print("Successfully connected to myDevices MQTT broker")
# register callback
client.on_message=on_message

def senddata():
  sht30Temperature, sht30Humidity = sht30.getTempAndHumi(clockStretching=SHT3X.NO_CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
  print("Temperature: %6.3f"%sht30Temperature)
  client.celsiusWrite(sht30TempChannel,sht30Temperature)
  client.celsiusWrite(sht30TempChannel+1,sht30Temperature)
  print("Relative humidity: %6.3f"%sht30Humidity + '%')
  client.humidityWrite(sht30HumidityChannel,sht30Humidity)
  client.humidityWrite(sht30HumidityChannel+1,sht30Humidity)  
count = 0
while True:
    try:
        client.loop()
        time.sleep(0.5)
        count += 1
        if count == 10:
            count = 0
            senddata()
    except OSError:
        pass
