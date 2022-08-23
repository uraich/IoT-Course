# ultrasonicRanging.py: Measures the time an ultrasonic wave needs to travel to
# a target and back
# Calculates the distance between the sensor and the target.
# Copyright (c) U. Raich
# This program is part of the IoT course at the University of Cape Coast, Ghana
# It is released under the MIT license

from hc_sr04 import HC_SR04

hc_sr04 = HC_SR04()
while True:
    echo_time = hc_sr04.measure()
    distance = hc_sr04.distance(echo_time)
    print("Distance: {:f} [cm]".format(distance))
