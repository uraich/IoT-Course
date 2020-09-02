#!/usr/bin/python3
# fit the adc data with a polynomial
import math
import matplotlib.pyplot as plt
import numpy as np
import numpy.polynomial.polynomial as pol
file = open("pltfile.dat","w")
# read the data from the measurement file
dac = np.arange(256)
adc = np.arange(0,4096,16)
print("range ADC: ",len(adc))
fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.set(xlabel='expected ADC value', ylabel='DAC value',
       title='Expected ADC vs DAC curve')
ax.plot(adc,dac)
plt.show()
