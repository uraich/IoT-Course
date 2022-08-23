# hcm5883_demo.py: Exercises the HCM5883 driver. Runs the self test and
# then reads the magnetometer values and calculate the heading
# Copyright U. Raich 11.8.2022
# Released under the MIT license
# This program is part of the IoT course at the University of Cape Coast, Ghana
#

from HMC5883 import HMC5883
from HMC5883_const import *
from time import sleep_ms

hmc5883 = HMC5883()
id = hmc5883.getID()
hmc5883.setAvg(HMC5883_AVG_8)
hmc5883.setBias(HMC5883_MS_NORMAL_BIAS)
hmc5883.setGain(HMC5883_GAIN_1_3)
hmc5883.setMode(HMC5883_MR_CONT)

hmc5883.printRegValues()
# hmc5883.setDebug(True)
hmc5883.selfTest()

# set the magnetic declination for Geneva
hmc5883.setMagneticDeclination(GENEVA_MAG_DECLINATION[0],
                               GENEVA_MAG_DECLINATION[1])

hmc5883.setBias(HMC5883_MS_NORMAL_BIAS)
sleep_ms(5000)

while True:
    if hmc5883.getRdy():
        data = hmc5883.getMag()
        degrees,minutes = hmc5883.getHeading()
        print("mag_x: {:10.4f} mG, mag_y: {:10.4f} mG, mag_z mG: {:10.4f}".format(1000*data[0],1000*data[1],1000*data[2]),end=", ")
        print("heading: {:d}° {:d}'".format(degrees,minutes))
        sleep_ms(500)

