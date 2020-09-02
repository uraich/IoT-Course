#!/usr/bin/python3
# fit the adc data with a polynomial
import math
import matplotlib.pyplot as plt
import numpy as np
file = open("pltfile.dat","w")
# read the data from the measurement file
calib = np.loadtxt("linearity.txt")
for i in range(5):
    print(calib[i])
print("length of calib:",len(calib))
# create the dac values

dac = np.arange(256)

for i in range(256):
    file.write("{:f} {:f}\n".format(calib[i],dac[i]))
file.close()
print("length of dac:",len(dac))
for i in range(5):
    print(dac[i])
    
coeff = np.polyfit(calib,dac,8)
for i in range(len(coeff)):
    print(coeff[i])

fitted = np.empty(256)

for i in range(256):
    fitted[i] = coeff[0]*math.pow(calib[i],8) + coeff[1]*math.pow(calib[i],7) + coeff[2]*math.pow(calib[i],6) + coeff[3]*math.pow(calib[i],5) +\
        coeff[4]*math.pow(calib[i],4) + coeff[5]*math.pow(calib[i],3)+coeff[6]*math.pow(calib[i],2)+coeff[7]*calib[i] + coeff[8] + 4
    # print(fitted[i])

fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.set(xlabel='ADC value', ylabel='DAC value',
       title='Polynomial fit to calibration')
ax.plot(calib,dac)
ax.plot(calib,fitted)
plt.show()
