# self_test.py: Starts the self test feature of the hmc5883 and checks that
# the values read back are within the expected range
# Copyright U. Raich 11.8.2022
# Released under the MIT license
# This program is part of the IoT course at the University of Cape Coast, Ghana
#

from HMC5883 import HMC5883
# from HMC5883_const import *

hmc5883 = HMC5883()
# hmc5883.setDebug(True)
hmc5883.setSmoothing(10)
hmc5883.selfTest()


