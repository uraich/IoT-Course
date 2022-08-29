# gain.py: changes the hmc5883 gain and reads the raw magnetometer values
# as well as the physical values, where the gain is taken into account
# Copyright (c) U. Raich 26. Aug 2022
# Released under the MIT license
# This program is part of the course on the Internet of Things at the
# University of Cape Coast, Ghana

from HMC5883_const import *
from HMC5883 import HMC5883
from time import sleep_ms

hmc5883 = HMC5883()
hmc5883.setAvg(HMC5883_AVG_8)
hmc5883.setBias(HMC5883_MS_NORMAL_BIAS)
hmc5883.setMode(HMC5883_MR_CONT)
hmc5883.setGain(HMC5883_GAIN_0_88)
hmc5883.setSmoothing(5)
hmc5883.printRegValues()
hmc5883.setSmoothing(10)
for gain in range(8):
    hmc5883.setGain(gain)
    print("Gain: {:d}".format(hmc5883.getGainInt()))
    magRaw = hmc5883.getMagRaw()
    print("mag raw: {:f}, {:f}, {:f}".format(magRaw[X],magRaw[Y],magRaw[Z]))
    mag = hmc5883.getMag()
    print("mag physical: {:f} mG, {:f} mG, {:f} mG".format(mag[X],mag[Y],mag[Z]))
    sleep_ms(500)
