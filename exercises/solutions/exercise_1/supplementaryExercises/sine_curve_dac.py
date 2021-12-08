#!/usr/bin/python3
# sine_curve.py: Calculates 100 points of a sine curve and prints out the
# values. You can re-direct the output to a file and plot it with gnuplot
# Copyright (c) U. Raich Nov. 2021
# This program is part of a course on IoT at the Korofidua Technical University, Ghana
#

from math import pi,sin

for index in range(100):
    angle = 2*pi*index/100  # this creates angles in radians 0 .. 2*pi
    sinDac = int(127*sin(angle) + 127)
    print(sinDac)
