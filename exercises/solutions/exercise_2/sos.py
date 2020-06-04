#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License

# This programs blinks an SOS on a LED. If used on the WeMos D1 ESP32 board the
# on-board LED is used

from machine import Pin
import time,sys

_LED_PIN = 2
_LONG  = 0.5
_SHORT = 0.2

led = Pin(_LED_PIN,Pin.OUT)

def pulse(pulseLength):
    led.on()
    time.sleep(pulseLength)
    led.off()
    time.sleep(pulseLength)

while True:
    try:
        for index in range(0,3):
            pulse(_SHORT)
        for index in range(0,3):
            pulse(_LONG)
        for index in range(0,3):
            pulse(_SHORT)
        time.sleep(1)
    except KeyboardInterrupt:
        print("Ctrl C seen! Switching LED off")
        led.off()
        sys.exit(0)
    

