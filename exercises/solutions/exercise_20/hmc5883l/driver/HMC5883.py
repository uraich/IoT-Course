# HCM5883.py: Controls the HCM5883 magnetometer through the I2C controller
# on the ESP32. It first checks if the HMC5883 is directly accessible by the
# I2C bus and if not it checks if the MPU6050 is on the bus.
# if yes, it disables the MPU6050 I2C controller and sets it to
# bypass mode.
# Then it accesses the HCM5883 registers directly
# Copyright U. Raich 11.8.2022
# Released under the MIT license
# This program is part of the IoT course at the University of Cape Coast, Ghana
#

from machine import Pin,I2C
from HMC5883_const import *

from time import sleep_ms
from math import atan2,floor,pi

MPU6050_ADDRESS     = const(0x68)
MPU6050_WHO_AM_I    = const(0x75)
MPU6050_PWR_MGMT_1  = const(0x6b)
MPU6050_USER_CTRL   = const(0x6a)
MPU6050_INT_PIN_CFG = const(0x37)

class HMC5883:
    def __init__(self,bus=1,scl=22,sda=21,drdy=27,debug=False):
        self.debug = debug
        self.drdy=Pin(drdy,Pin.IN)
        self.declination = (0,0)
        self.smoothing = 1
        self.mag_x = self.mag_y = self.mag_z = None
        # Create an I2C object
        # Check if we can use the hardware I2C interface, if not, create a software I2C interface
        if bus == 1:
            if self.debug:
                print("Running on I2C hardware interface with bus = ",bus, "scl = ",scl, " sda = ",sda)
            self.i2c = I2C(bus,scl=Pin(scl),sda=Pin(sda))
        else:
            if self.debug:
                print("Running on I2C bus ",bus, "scl = ",scl, " sda = ",sda)
            self.i2c = SoftI2C(scl,sda)
            
        addr = self.i2c.scan()
        # print(addr)
        # check if the HMC5883 is accessible directly or if it is on the MPU6050 I2C master
        if HMC5883_ADDRESS in addr:
            if self.debug:
                print("HMC5883 is accessible directly")
            return
            
        if not MPU6050_ADDRESS in addr:
            raise Exception("Cannot find MPU6050 on the I2C bus")
        else:
            if self.debug:
                print("HMC5883 is accessible via the MCU6050")                
        
        # get MPU6050 out of sleep mode
        self.writeByte(MPU6050_PWR_MGMT_1,0,mpu6050=True)
        # read the WHO_AM_I register on the MPU6050
        who_am_i = self.readByte(MPU6050_WHO_AM_I,mpu6050=True)
        if self.debug:
            print("who_am_i on MPU6050: 0x{:02x}".format(who_am_i))
        if who_am_i != MPU6050_ADDRESS:
            raise Exception("Chip is not an MPU6050")

        # disable I2C master
        self.writeByte(MPU6050_USER_CTRL,0,mpu6050=True)
        # enable bypass
        self.writeByte(MPU6050_INT_PIN_CFG,0x02,mpu6050=True)
        
        # re-scan the I2C bus. Now we should find the HCM5883
        addr = self.i2c.scan()
        if self.debug:
            print("Modules found on the I2C bus at addresses: ",end="")
            for i in range(len(addr)):
                print("0x{:02x} ".format(addr[i]),end="")
            print("")
        if not HMC5883_ADDRESS in addr:
            raise Exception("No HCM5883 module in the I2C bus")

    def setDebug(self,onOff):
        if onOff:
            print("Switch debug on")
        else:
            print("Switch debug off")
        self.debug = onOff

    def readBytes(self,register,no_of_bytes,mpu6050=False):
        if mpu6050:
            i2c_address = MPU6050_ADDRESS
        else:
            i2c_address = HMC5883_ADDRESS
        data = self.i2c.readfrom_mem(i2c_address,register,no_of_bytes)
        if self.debug:
            if mpu6050:
                print("readBytes: reading from MPU6050 register 0x{:02x} ".format(register),end="")
            else:
                print("readBytes: reading from HMC5883 register 0x{:02x} ".format(register),end="")
            for i in range(no_of_bytes):
                print("0x{:02x} ".format(data[i]),end="")
            print("")
        return data

    def writeBytes(self,register,values,mpu6050=False):
        if mpu6050:
            i2c_address = MPU6050_ADDRESS
        else:
            i2c_address = HMC5883_ADDRESS

        if self.debug:
            if mpu6050:
                print("writeBytes: writinging to MPU6050 register 0x{:02x}".format(register),end="")
            else:
                print("writeBytes: writinging to HMC5883 register 0x{:02x}".format(register),end="")
            for i in range(len(values)):
                print("0x{:02x} ".format(values[i]),end="")
            print("")
        self.i2c.writeto_mem(i2c_address,register,values)

    def readByte(self,register,mpu6050=False):
        return self.readBytes(register,1,mpu6050)[0]

    def writeByte(self,register,value,mpu6050=False):
        tmp = bytearray(1)
        tmp[0] = value
        self.writeBytes(register,tmp,mpu6050)

    def readBits(self, register, bit_position, no_of_bits,mpu6050=False):
        if mpu6050:
            i2c_address = MPU6050_ADDRESS
        else:
            i2c_address = HMC5883_ADDRESS
        tmp = self.readByte(register,mpu6050)
        mask = 1
        for i in range(1,no_of_bits):
            mask = mask << 1 | 1
        shift = bit_position - no_of_bits + 1
        mask <<= shift        
        # print("mask: 0x{:02x}".format(mask))
        tmp &= mask
        return tmp >> shift

    def readBit(self,register,bit_position,mpu6050=False):
        return self.readBits(register,bit_position,1,mpu6050)

    def writeBits(self,register,bit_position,no_of_bits, value, mpu6050=False):
        if mpu6050:
            i2c_address = MPU6050_ADDRESS
        else:
            i2c_address = HMC5883_ADDRESS
        # print("writeBits: value: 0x{:02x}".format(value))   
        tmp = self.readByte(register,mpu6050)
        if self.debug:
            if mpu6050:
                print("writeBits: read from mpu6050 register 0x{:02x}: 0x{:02x}".format(register,tmp))
            else:
                print("writeBits: read from hmc5883 register 0x{:02x}: 0x{:02x}".format(register,tmp))
        mask = 1
        for i in range(1,no_of_bits):
            mask = mask << 1 | 1
        shift = bit_position - no_of_bits + 1
        mask <<= shift        
        # print("mask: 0x{:02x}".format(mask))
        mask = ~ mask
        tmp &= mask
        tmp |= value <<shift
        if self.debug:
            if mpu6050:
                print("writeBits: Writing 0x{:02x} to register 0x{:02x} on mpu6050".format(tmp,register))
            else:
                print("writeBits: Writing 0x{:02x} to register 0x{:02x} on hmc5883".format(tmp,register))
        self.writeByte(register,tmp)
        
    def getID(self):
        id = self.readBytes(HMC5883_ID_A,3).decode()
        if self.debug:
            print("ID: ",id)
        return id
    
    def mag_declination_rad(self,degrees,minutes):
        # calculate the magnetic declination in radians from degrees and minutes
        decimalDegrees = degrees + minutes/60
        mag_decl_rad = 2*pi*decimalDegrees/360
        if self.debug:
            print("decimal degrees: {:8.4f}".format(decimalDegrees))
            print("magnetic declination in radians: {:8.4f}".format(mag_decl_rad))
        return mag_decl_rad

    def setMagneticDeclination(self,degrees,minutes): 
        self.declination=(degrees,minutes)
        
    def getMagneticDeclination(self): 
        return self.declination[0], self.declination[1]
        
    # config A register

    def getConfig_A(self):
        return self.readByte(HMC5883_CONF_A)
    
    def setConfig_A(self,value):
        return self.writeByte(HMC5883_CONF_A,value)
    
    def getAvg(self):
        return self.readBits(HMC5883_CONF_A,HMC5883_MA_POS,HMC5883_MA_SIZE)

    def getAvgInt(self):
        return HMC5883_average[self.readBits(HMC5883_CONF_A,HMC5883_MA_POS,HMC5883_MA_SIZE)]

    def setAvg(self,value):
        # print("setAvg: value: 0x{:02x}".format(value))
        self.writeBits(HMC5883_CONF_A,HMC5883_MA_POS,HMC5883_MA_SIZE,value)

    def getSamplingRate(self):
        return self.readBits(HMC5883_CONF_A,HMC5883_DO_POS,HMC5883_DO_SIZE)

    def getSamplingRateFloat(self):
        return HMC5883_dataRate[self.readBits(HMC5883_CONF_A,HMC5883_DO_POS,HMC5883_DO_SIZE)]
    
    def setSamplingRate(self,value):
        self.writeBits(HMC5883_CONF_A,HMC5883_DO_POS,HMC5883_DO_SIZE,value)

    def getBias(self):
        return self.readBits(HMC5883_CONF_A,HMC5883_MS_POS,HMC5883_MS_SIZE)

    def getBiasStr(self):
        return HMC5883_bias[self.readBits(HMC5883_CONF_A,HMC5883_MS_POS,HMC5883_MS_SIZE)]

    def setBias(self,value):
        self.writeBits(HMC5883_CONF_A,HMC5883_MS_POS,HMC5883_MS_SIZE,value)

    # config B register
    
    def getConfig_B(self):
        return self.readByte(HMC5883_CONF_B)
    
    def setConfig_B(self,value):
        return self.writeByte(HMC5883_CONF_B,value)

    def getGain(self):
        return self.readBits(HMC5883_CONF_B,HMC5883_GAIN_POS,HMC5883_GAIN_SIZE)

    def getGainInt(self):
        return HMC5883_gain[self.readBits(HMC5883_CONF_B,HMC5883_GAIN_POS,HMC5883_GAIN_SIZE)]

    def setGain(self,value):
        tmp = value << (HMC5883_GAIN_POS - HMC5883_GAIN_SIZE +1)
        if self.debug:
            print("setGain: code: 0x{:02x}".format(tmp))
        self.writeByte(HMC5883_CONF_B,tmp)
        # dummy read the last values
        self.getMagRaw()
        sleep_ms(200)

    # mode register

    def getMode(self):
        return self.readBits(HMC5883_MODE,HMC5883_MR_POS,HMC5883_MR_SIZE)

    def setMode(self,value):
        tmp = value & 0x3
        self.writeByte(HMC5883_MODE,tmp)

    # status register

    def getStatus(self):
        return self.readByte(HMC5883_STATUS)

    def getLock(self):
        return self.readBit(HMC5883_STATUS,HMC5883_STS_LOCK)

    def getDataReady(self):
        return self.readBit(HMC5883_STATUS,HMC5883_STS_RDY)


    def getMag16Bits(self):
        data = self.readBytes(HMC5883_DATA_X_MSB,6)
        mag_x = data[0] << 8 | data[1]
        # careful: the sequence is x,z,y !!!
        mag_z = data[2] << 8 | data[3]
        mag_y = data[4] << 8 | data[5]
        return (mag_x,mag_y,mag_z)

    def getMagRaw(self):
        magRaw = [0]*3
        # dummy read to be sure we get the latest values
        data = self.getMag16Bits()
        # apply smoothing if smoothing value is set        
        if self.debug:
            print("getMagRaw: Averaging over {:d} measurements".format(self.smoothing))
        for _ in range(self.smoothing):
            # check data ready
            timeout = 0
            while not self.getDataReady() and timeout < 200: # should not take langer than 200 ms
                timeout += 1
                sleep_ms(1)
            if timeout >= 200:
                raise Exception ("Acquisition timeout")
            
            tmp = list(self.getMag16Bits())
            for axis in range(3):
                if tmp[axis] & 0x8000:
                    tmp[axis] -= 0x10000
                magRaw[axis] += tmp[axis]
        for axis in range(3):
            magRaw[axis] /= self.smoothing
        if self.debug:
            print("getMagRaw: mag raw: {:8.2f}, {:8.2f}, {:8.2f}".format(magRaw[X],magRaw[Y],magRaw[Z]))
        self.mag_x = magRaw[X]
        self.mag_y = magRaw[Y]
        self.mag_z = magRaw[Z]
        return tuple(magRaw)
    
    def getMagRaw_x(self):
        return self.getMagRaw()[X]

    def getMagRaw_y(self):
        return self.getMagRaw()[Y]

    def getMagRaw_Z(self):
        return self.getMagRaw()[Z]
    
    def getMag(self):
        data = self.getMagRaw()
        # print("getMag: raw data {:f}, {:f}, {:f}".format(data[X],data[Y],data[Z]))
        coeff = HMC5883_gain[self.getGain()]
        # print("getMag: coeff: {:d}".format(coeff))
        if self.debug:
            print("gain scaling factor: {:f}".format(coeff))
        self.mag_x = 1000*data[X]/coeff # values in mG
        self.mag_y = 1000*data[Y]/coeff
        self.mag_z = 1000*data[Z]/coeff
        # print("getMag: mag: {:f}, {:f}, {:f}".format(self.mag_x,self.mag_y,self.mag_z)) 
        return (self.mag_x,self.mag_y,self.mag_z)
    
    def getMag_x(self):
        return self.getMag()[X]

    def getMag_y(self):
        return self.getMag()[Y]

    def getMag_z(self):
        return self.getMag()[Z]

    def getHeading(self):
        if self.mag_x == None or self.mag_y == None:
            return
        heading_rad = atan2(self.mag_y, self.mag_x)
        heading_rad -= self.mag_declination_rad(self.declination[0],
                                                self.declination[1])
        # Correct reverse heading.
        if heading_rad < 0:
            heading_rad += 2 * pi

        # Compensate for wrapping.
        elif heading_rad > 2 * pi:
            heading_rad -= 2 * pi
            
        # Convert from radians to degrees.
        heading = heading_rad * 180 / pi
        degrees = floor(heading)
        minutes = round((heading - degrees) * 60)
        return int(degrees), int(minutes)

    def setSmoothing(self,value):
        self.smoothing = value

    def getSmoothing(self):
        return self.smoothing
    
    # interrupts

    def drdyHandler(self,src):
        data = self.getMagRaw()
        print("mag_x: {:d}, mag_y: {:d}, mag_z: {:d}".format(data[0],data[1],data[2]))
        
    def enbleDrdyInt(self):
        self.drdy.irq(trigger=Pin.IRQ_RISING,handler=drdyHandler)

    def disableDrdyInt(self):
        self.drdy.irq(trigger=Pin.IRQ_RISING,handler=None)

    # self test

    def selfTest(self):
        LOW_LIMIT = 243
        HIGH_LIMIT = 575
        failed=False
        self.setConfig_A(0x71)   # 8-average, 15 Hz, positive test measurement
        self.setGain(5)
        self.setMode(0)
        data = self.getMagRaw()
        failed=False
        for axis in range(3):
            if data[axis] < LOW_LIMIT or data[axis] > HIGH_LIMIT:
                failed=True
        if failed:
            print("Self test failed")
            print("Self test, positive offset: mag_x: {:f}, mag_y: {:f}, mag_z: {:f}".format(data[X],data[Y],data[Z]))
            return False
        print("Self test successful")
        if self.debug:
            print("Self test, positive offset: mag_x: {:f}, mag_y: {:f}, mag_z: {:f}".format(data[X],data[Y],data[Z]))
        return True
     
    def printRegValues(self):
        print("================ register values ===================")
        print("Configuration A: 0x{:02x}".format(self.getConfig_A()))
        print("Averaging {:d} values".format(self.getAvgInt()))
        print("Data rate: {:4.1f} Hz".format(self.getSamplingRateFloat()))
        print("Bias: ",self.getBiasStr())
        print("")
        print("Configuration B: 0x{:02x}".format(self.getConfig_B()))
        print("Gain: {:d}".format(self.getGainInt()))
        print("")
        print("Mode: 0x{:02x}".format(self.getMode()))
        
