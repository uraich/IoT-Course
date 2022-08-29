# leds.py: the beginnings of a driver for the tcs3200 light sensor
# Copyright (c) U. Raich
# Written for the course on the Internet of Things at the
# University of Cape Coast, Ghana
# The program is released under the MIT licence

from tcs3200 import TCS3200

# create an TCS3200 object
tcs3200 = TCS3200(OUT=19, S2=5, S3=18, S0=17, S1=16, LED=23)
# set debugging on
tcs3200.debugging=tcs3200.ON
# check if it has really been switched on
if tcs3200.debugging:
    print("debugging is on")
else:
    print("debugging is on")

# switch the LEDs off
tcs3200.led=tcs3200.OFF
