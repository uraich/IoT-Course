#!/usr/bin/python3
# sine_curve_plot.py: Calculates 100 points of a sine curve and creates a
# graph with matplotlib
# These values can be sent to a DAC to produce a sinusoidal signal
# Copyright (c) U. Raich Nov. 2021
# This program is part of a course on IoT at the Korofidua Technical University, Ghana
#

from math import pi,sin
import matplotlib.pyplot as plt
# create a list for the angles and another one for the corresponding sin values
angles = []
sinValues = []
for index in range(100):
    # fill the lists
    angle = 2*pi*index/100  # this creates angles in radians 0 .. 2*pi
    angles.append(angle)
    sinValues.append(sin(angle))
print(len(angles),len(sinValues))

plt.plot(angles,sinValues)
# now plot the data
# naming the x axis
plt.xlabel('angle in radians')
# naming the y axis
plt.ylabel('sin')

# giving a title to my graph
plt.title('The sin function')

plt.show()
