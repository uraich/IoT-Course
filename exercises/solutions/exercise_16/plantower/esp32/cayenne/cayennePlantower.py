# cayennePlantower
# Reads out the Plantower dust sensor and sends the data to
# to Cayenne. 
# copyright U. Raich
#
# Released under GPL
#

from machine import Pin
import cayenne.client
import sys,time

import ulogging as logging
from plantower import PlanTower

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "7c70a330-69af-11e8-a76a-fdebb8d0010d"
MQTT_PASSWORD  = "32d184add41570759dd1735fa464cef7e62876a4"
MQTT_CLIENT_ID = "f1c681c0-bcab-11eb-883c-638d8ce4c23d"

channel = 0

client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO)
print("Successfully connected to myDevices MQTT broker")
# register callback
# client.on_message=on_message

count = 0
while True:
    try:
        client.loop()
        time.sleep(0.5)
        count += 1
        if count == 10:
            count = 0
            # senddata()
    except OSError:
        pass
