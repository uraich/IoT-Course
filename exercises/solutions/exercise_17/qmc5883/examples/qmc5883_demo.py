# qmc5883_demo.py: demonstrates the use use of the QMC5883 driver
# Copyright U. Raich, 25.8.2020
# This program is released under he MIT license
# It is part of the course on the Internet of Things at
# the University of Cape Coast, Ghana

from QMC5883_const import *
from QMC5883 import QMC5883
from utime import sleep_ms

qmc5883 = QMC5883()

# qmc5883.setRange(QMC5883_8G)
# qmc5883.setDebug(True)
qmc5883.setCtrl_1(0x1d)
print("ctrl1: 0x{:02x}".format(qmc5883.getCtrl_1()))
qmc5883.printRegValues()
qmc5883.setDebug(False)
qmc5883.setSmoothing(10)
# Switch to contious mode
qmc5883.setMode(QMC5883_MODE_NORMAL)
print("Mode after setting to continuous: ",QMC5883_MODE[qmc5883.getMode()])
print("Control register 1: 0x{:02x}".format(qmc5883.getCtrl_1()))
# qmc5883.setDebug(True)

sleep_ms(5000)
while True:
    if qmc5883.getDataReady():
        data = qmc5883.getMagRaw()
        temp = qmc5883.getTempRaw()
        print("mag_x: {:8.2f}, mag_y: {:8.2f}, mag_z: {:8.2f}, temperature: {:d}".format(data[0],data[1],data[2],temp))
        # data = qmc5883.getMag()
        # degrees,minutes = qmc5883.getHeading()
        # print("mag_x: {:8.4f} mG, mag_y: {:8.4f} mG,mag_z: {:8.4f} mG, heading: {:d}°, {:d}'".format(
        #     data[0],data[1],data[2],degrees,minutes))
        # data = qmc5883.getMag16Bits()
        # print("mag_x: 0x{:04x} mG, mag_y: 04{:04x} mG, mag_z: 0x{:04x} mG".format(
        #     data[0],data[1],data[2]))

        sleep_ms(500)

