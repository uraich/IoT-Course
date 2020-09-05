# mqttSubLed.py
# subscribes to the "DCSIT" topic waiting for a payload of either
# "LED on"
# or
# "LED off"
# If such a payload is seen the corresponding action is executed on the WeMos D1 built-in LED
# This is a solution to exercise 2 of session 3 for the workshop on IoT
# at the African Internet Summit 2019 in Kampala, Uganda
# Copyright Uli Raich, 28. May 2019
# The program is released under GPL

from umqtt.simple import MQTTClient
from machine import Pin
from wifi_connect import *

led=Pin(19,Pin.OUT)

# Send the command with
# mosquitto_pub -t "DCSIT" -m "LED on"

SERVER="192.168.1.36"
TOPIC=b"DCSIT"

def cmdCallback(topic,payload):
    print(topic,payload)
    if payload == b"LED on":
        led.value(1)
        print("Switch LED on")
    elif payload == b"LED off":
        led.value(0)
        print("Switch LED off");

connect()

c = MQTTClient("umqtt_client", SERVER)
c.connect()

c.set_callback(cmdCallback)
c.subscribe("DCSIT")

print("Waiting for messages for topic 'DCSIT' from the MQTT broker")
while True:
    c.wait_msg()
