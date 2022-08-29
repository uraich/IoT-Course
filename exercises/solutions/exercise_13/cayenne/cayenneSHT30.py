#
# cayenneSHT30.py
# Reads out the SHT30 temperature and humidity and sends the measurement
# to Cayenne
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
MQTT_USERNAME  = "7c70a330-69af-11e8-a76a-fdebb8d0010d"
MQTT_PASSWORD  = "32d184add41570759dd1735fa464cef7e62876a4"
MQTT_CLIENT_ID = "dae86710-4ae9-11e9-a6b5-e30ec853fbf2"

sht30TempChannel = 5
sht30HumidityChannel = 6

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

def senddata():
  sht30Temperature, sht30Humidity = sht30.getTempAndHumi(clockStretching=SHT3X.NO_CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
  print("Temperature: %6.3f"%sht30Temperature)
  client.celsiusWrite(sht30TempChannel,sht30Temperature)
  time.sleep(5)
  print("Relative humidity: %6.3f"%sht30Humidity + '%')
  client.humidityWrite(sht30HumidityChannel,sht30Humidity)
  time.sleep(5)
  
while True:
    try:
        senddata()
    except OSError:
        pass
