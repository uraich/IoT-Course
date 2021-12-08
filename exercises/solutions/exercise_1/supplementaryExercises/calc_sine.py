#!/usr/bin/python3
# calc_sine.py: Ask the user to enter an angle in degrees, convert it to radians
# and output the sin(angle)
# Copyright (c) U. Raich Nov. 2021
# This program is part of a course on IoT at the Korofidua Technical University, Ghana
# 

from math import pi,radians,sin
import sys

print("Please give an angle in degrees (0..360) --> ",end='')
angleTxt = input()
try:
    angle = float(angleTxt)
except:
    print(angleTxt," is not a valid angle, please re-try")
    sys.exit(-1)
if angle < 0 or angle > 360:
    print("Please restrict you angle to the range 0..360")
    sys.exit(-1)
print("sin(",angle,") = ",sin(radians(angle)))
