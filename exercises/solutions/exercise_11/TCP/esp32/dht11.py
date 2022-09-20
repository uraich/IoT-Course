#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License

# This program reads out the DHT11 on a WeMos D1 ESP32 module

import dht
from machine import Pin
import time,sys

_DHT11_PIN = 22

dht11 = dht.DHT11(Pin(_DHT11_PIN))

try:
    while True:
        dht11.measure()
        temperature = dht11.temperature()
        relHumidity = dht11.humidity()
        print("Temperature: %d °C"%temperature)
        print("Relative Humidity: %d %%"%relHumidity)
        time.sleep(2)
except KeyboardInterrupt:
    print("Ctrl C seen! Returning to REPL")
    sys.exit(0)
