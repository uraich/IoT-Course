# mqttPub.py
# a program publishing "Welcome to the DCSIT IoT course" to topic
# "AFNOG19" on a PC running mosquitto
# The IP address of the PC must be known
# This is the solution to exercise 2 of the exercises on MQTT and Cayenne
# of the IoT course at the University of Cape Coast, Ghana
# The program was originally written for the IoT workshop at
# the African Internet Summit 2019, Kampala, Uganda
# Copyright Uli Raich 28.5.2019
# The program is released under GPL

from umqtt.simple import MQTTClient
import network
import time
from wifi_connect import *

# Test reception e.g. with:
# mosquitto_sub -t "DCSIT"

SERVER="192.168.1.36"
TOPIC=b"DCSIT"
PAYLOAD=b"Welcome to the DCSIT IoT course"

connect()

c = MQTTClient("umqtt_client", SERVER)
c.connect()
for i in range(0,10):
    c.publish(TOPIC, PAYLOAD)
    time.sleep(1)
c.disconnect()
