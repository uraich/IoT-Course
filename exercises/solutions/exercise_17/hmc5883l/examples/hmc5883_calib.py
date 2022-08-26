# hmc5883_calib.py: Calibrates the magnetometer
# When turning the magnetometer around the x,y,z axis the measured values
# should switch from one axis to the other.
# Copyright U. Raich, 25.8.2020
# This program is released under he MIT license
# It is part of the course on the Internet of Things at
# the University of Cape Coast, Ghana

from HMC5883_const import *
from HMC5883 import HMC5883
from utime import sleep_ms

hmc5883 = HMC5883()

hmc5883.setAvg(HMC5883_AVG_8)
hmc5883.setBias(HMC5883_MS_NORMAL_BIAS)
hmc5883.setGain(HMC5883_GAIN_1_3)
hmc5883.setMode(HMC5883_MR_CONT)
hmc5883.setSmoothing(5)
# hmc5883.printRegValues()
# hmc5883.setDebug(True)

# print("Gain set to {:d}".format(hmc5883.getGainInt()))
data = hmc5883.getMagRaw()
# print("raw: {:8.2f}, {:8.2f}, {:8.2f}".format(data[X],data[Y],data[Z]))
data = hmc5883.getMag()
# print("{:8.2f}, {:8.2f}, {:8.2f}".format(data[X],data[Y],data[Z]))

'''
print("Setting mode to idle and changing the gain")
hmc5883.setMode(HMC5883_MR_IDLE)
hmc5883.setGain(HMC5883_GAIN_5_6)
print("Gain set to {:d}".format(hmc5883.getGainInt()))

hmc5883.setMode(HMC5883_MR_CONT)
data = hmc5883.getMagRaw()
print("raw: {:8.2f}, {:8.2f}, {:8.2f}".format(data[X],data[Y],data[Z]))
data = hmc5883.getMag()
print("{:8.2f}, {:8.2f}, {:8.2f}".format(data[X],data[Y],data[Z]))

'''
while True:
    # data = hmc5883.getMagRaw()
    # print("{:8.2f}, {:8.2f}, {:8.2f}".format(data[0],data[1],data[2]))
    data = hmc5883.getMag()
    # degrees,minutes = hmc5883.getHeading()
    # print("mag_x: {:8.4f} mG, mag_y: {:8.4f} mG,mag_z: {:8.4f} mG, heading: {:d}°, {:d}'".format(
    #     data[0],data[1],data[2],degrees,minutes))
    print("{:8.2f}, {:8.2f}, {:8.4f}".format(data[X],data[Y],data[Z]))
    # data = qmc5883.getMag16Bits()
    # print("mag_x: 0x{:04x} mG, mag_y: 04{:04x} mG, mag_z: 0x{:04x} mG".format(
        #     data[0],data[1],data[2]))

    sleep_ms(500)

