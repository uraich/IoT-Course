#
# cayenneDummy.py
# Simulates temperature measurements and send the values 
# to Cayenne
# copyright U. Raich
# This is a demo program for the workshop on IoT at the
# African Internet Summit 2019, Kampala
# Released under GPL
#
from machine import Pin
import cayenne.client
import sys,time
from random import random
import ulogging as logging

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "your mqtt user code"
MQTT_PASSWORD  = "your mqtt password code"
MQTT_CLIENT_ID = "your mqtt client id"

dummyTempChannel = 0

client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO)
print("Successfully connected to myDevices MQTT broker")

def senddata():
  dummyTemperature = 25.0 + 10*random()      # add a random value between 0 and 10
  print("Temperature: %6.3f"%dummyTemperature)
  client.celsiusWrite(dummyTempChannel,dummyTemperature)
  time.sleep(2)
  
while True:
    try:
        senddata()
    except OSError:
        pass
