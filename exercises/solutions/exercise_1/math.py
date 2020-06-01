#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License
# Demonstrates the calculation of sin when the parameter is given in degrees

# Calculate the sin function
import sys,math

def getAngleDeg():
    while True:
        try:
            numString = input()
            angleDeg=float(numString)
        except ValueError:
            print(numString," is not an float number, please give a new one: ",end="")
            getAngleDeg()
        
        return angleDeg
    
print("Calculating the sin function")
print("Please enter the angle in degrees: ",end="")

angleDeg = getAngleDeg()
angle = float(angleDeg)
angle = angle * 2 * math.pi / 360

print("angle in radian:      %10.4f"%angle)
print("Sin of %s degrees is: %10.4f\n"%(angleDeg,math.sin(angle)))
