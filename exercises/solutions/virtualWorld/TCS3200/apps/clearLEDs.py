# clearLeds.py: switches the illumination LEDs on the TCS3200 off
# Copyright (c) U. Raich
# Written for the course on the Internet of Things at the
# University of Cape Coast, Ghana
# The program is released under the MIT licence

from machine import Pin
LEDS_PIN = 23
illumLeds = Pin(LEDS_PIN,Pin.OUT)

illumLeds.off()
# or
'''
# create an TCS3200 object
tcs3200 = TCS3200(OUT=19, S2=5, S3=18, S0=17, S1=16, LED=LEDS_PIN)

# switch the LEDs off
tcs3200.led=tcs3200.OFF
'''
