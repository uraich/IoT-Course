#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License

# This programs blinks a LED. If used on the WeMos D1 ESP32 board the
# on-board LED is used 

from machine import Pin
import time,sys

_LED_PIN = 2

led = Pin(_LED_PIN,Pin.OUT)

try:
    while True:
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Ctrl C seen! Switching LED off")
    led.off()
    sys.exit(0)
