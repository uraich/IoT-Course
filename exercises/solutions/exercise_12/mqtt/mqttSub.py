from umqtt.simple import MQTTClient
import network
import time
from wifi_connect import *

# Test reception e.g. with:
# mosquitto_sub -t "DCSIT"


SERVER="192.168.1.36"
TOPIC=b"DCSIT"

def cmdCallback(topic,payload):
    print(topic,payload)
    
connect()

c = MQTTClient("umqtt_client", SERVER)
c.connect()

c.set_callback(cmdCallback)
c.subscribe("DCSIT")

print("Waiting for messages on topic 'DCSIT' from MQTT broker")
while True:
    c.wait_msg()
