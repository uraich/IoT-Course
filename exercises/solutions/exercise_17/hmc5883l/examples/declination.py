# declination.py: check the conversion routines for the magnetic declination
# Copyright U. Raich, 23.8.2022
# Released under the MIT license
# This prrogram is part of the IoT course at the University of Cape Coast, Ghana

from HMC5883_const import *
from HMC5883 import HMC5883

hmc5883 = HMC5883()
hmc5883.setMagneticDeclination(GENEVA_MAG_DECLINATION[0],
                               GENEVA_MAG_DECLINATION[1])
degrees,minutes = hmc5883.getMagneticDeclination()
print ("Magnetic declination in Geneva: {:d}° {:d}'".format(degrees,minutes))
hmc5883.setDebug(True)

print("Magnetic declination in rad: {:8.4f}".format(
    hmc5883.mag_declination_rad(degrees,minutes)))

print("Magnetic declination of 0° 0' in rad: {:8.4f}".format(
    hmc5883.mag_declination_rad(0,0)))
       
