# QCM5883.py: Controls the QCM5883 magnetometer
# Then it accesses the HCM5883 registers directly
# Copyright U. Raich 11.8.2022
#

from machine import Pin,I2C
from QMC5883_const import *

from time import sleep_ms
from math import atan2,floor,pi

class QMC5883:
    def __init__(self,bus=1,scl=22,sda=21,drdy=27,debug=False):
        self.debug = debug
        self.drdy=Pin(drdy,Pin.IN)
        self.declination = (0,0)
        self.mag_x = self.mag_y = self.mag_z = None
        self.smoothing = 1
        
        # Create an I2C object
        # Check if can use the hardware I2C interface, if not, create a software I2C interface
        if bus == 1:
            if self.debug:
                print("Running on I2C hardware interface with bus = ",bus, "scl = ",scl, " sda = ",sda)
            self.i2c = I2C(bus,scl=Pin(scl),sda=Pin(sda))
        else:
            if self.debug:
                print("Running on I2C bus ",bus, "scl = ",scl, " sda = ",sda)
            self.i2c = SoftI2C(scl,sda)
            
        addr = self.i2c.scan()
        if QMC5883_ADDRESS not in addr:
            raise Exception("QMC5883 not found on the I2C bus")
        else:
            if self.debug:
                print("QMC5883 is ready")

        # soft reset the chip
        self.softReset()
        sleep_ms(50)       # max power on 

        # write the set/reset period register with 0x02 (see data sheet)
        self.setSetResetPeriod(0x01)

    def setDebug(self,onOff):
        if onOff:
            print("Switch debug on")
        else:
            print("Switch debug off")
        self.debug = onOff

    def readBytes(self,register,no_of_bytes):
        data = self.i2c.readfrom_mem(QMC5883_ADDRESS,register,no_of_bytes)
        if self.debug:
            print("readBytes: reading from QMC5883 register 0x{:02x} ".format(register),end="")
            for i in range(no_of_bytes):
                print("0x{:02x} ".format(data[i]),end="")
            print("")
        return data

    def writeBytes(self,register,values):

        if self.debug:
            print("writeBytes: writing to QMC5883 register 0x{:02x}:".format(register),end=" ")
            for i in range(len(values)):
                print("0x{:02x} ".format(values[i]),end="")
            print("")
        self.i2c.writeto_mem(QMC5883_ADDRESS,register,values)

    def readByte(self,register):
        return self.readBytes(register,1)[0]

    def writeByte(self,register,value):
        tmp = bytearray(1)
        tmp[0] = value
        self.writeBytes(register,tmp)

    def readBits(self, register, bit_position, no_of_bits):
        tmp = self.readByte(register)
        mask = 1
        for i in range(1,no_of_bits):
            mask = mask << 1 | 1
        shift = bit_position - no_of_bits + 1
        mask <<= shift        
        # print("mask: 0x{:02x}".format(mask))
        tmp &= mask
        return tmp >> shift

    def readBit(self,register,bit_position):
        return self.readBits(register,bit_position,1)

    def writeBits(self,register,bit_position,no_of_bits, value):

        # print("writeBits: value: 0x{:02x}".format(value))   
        tmp = self.readByte(register)
        if self.debug:
            print("writeBits: read from qmc5883 register 0x{:02x}: 0x{:02x}".format(register,tmp))
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
            print("writeBits: Writing 0x{:02x} to register 0x{:02x} on qmc5883".format(tmp,register))
        self.writeByte(register,tmp)

    def writeBit(self,register,bit_position,value):
        self.writeBits(register,bit_position,1,value)
                       
    # ID register: should return 0xff
    
    def getID(self):
        id = self.readByte(QMC5883_ID)
        if self.debug:
            print("ID: ",id)
        return id
    
    # Status register
    def getStatus(self):
        return self.readByte(QMC5883_STATUS)

    def getDataSkip(self):
        return self.readBit(QMC5883_STATUS,QMC5883_STS_DOR)

    def getOverflow(self):
        return self.readBit(QMC5883_STATUS,QMC5883_STS_OVL)
    
    def getDataReady(self):
        return self.readBit(QMC5883_STATUS,QMC5883_STS_DRDY)

    # Control register 1 

    def getCtrl_1(self):
        # print("getCtrl_1 : register 0x{:02x}".format(QMC5883_CTRL_1))
        return self.readByte(QMC5883_CTRL_1)

    def setCtrl_1(self,value):
        self.writeByte(QMC5883_CTRL_1,value)

    def getOversampling(self):
        return self.readBits(QMC5883_CTRL_1,QMC5883_OSR_POS,QMC5883_OSR_SIZE)

    def setOversampling(self,value):
        self.writeBits(QMC5883_CTRL_1,QMC5883_OSR_POS,QMC5883_OSR_SIZE,value)

    def getRange(self):
        return self.readBits(QMC5883_CTRL_1,QMC5883_RNG_POS,QMC5883_RNG_SIZE)

    def setRange(self,value):
        if value != QMC5883_2G and value != QMC5883_8G:
            print("Illegal range, not set")
            return
        self.writeBits(QMC5883_CTRL_1,QMC5883_RNG_POS,QMC5883_RNG_SIZE,value)

    def getOutputRate(self):
        return self.readBits(QMC5883_CTRL_1,QMC5883_ODR_POS,QMC5883_ODR_SIZE)

    def setOutputRate(self,value):
        self.writeBits(QMC5883_CTRL_1,QMC5883_ODR_POS,QMC5883_ODR_SIZE,value)

    def getMode(self):
        return self.readBits(QMC5883_CTRL_1,QMC5883_MODE_POS,QMC5883_MODE_SIZE)

    def setMode(self,value):
        if value != QMC5883_MODE_STDBY and value != QMC5883_MODE_NORMAL:
            print("Illegal Mode, not set")
            return
        self.writeBits(QMC5883_CTRL_1,QMC5883_MODE_POS,QMC5883_MODE_SIZE,value)

    # Control register 2 

    def getCtrl_2(self):
        return self.readByte(QMC5883_CTRL_2)

    def setCtrl2(self,value):
        self.writeByte(QMC5883_CTRL_2,value)

    def getIntEnable(self):
        return self.readBit(QMC5883_CTRL_2,QMC5883_INT_ENB)

    def setIntEnable(self,value):
        self.writeBit(QMC5883_CTRL_2,QMC5883_INT_ENB)

    def softReset(self):
        self.writeBit(QMC5883_CTRL_2,QMC5883_SOFT_RESET,1)

    def getRollOver(self):
        return self.readBit(QMC5883_CTRL_2,QMC5883_ROL_PNT)

    def setRollOver(self,value):
        self.writeBit(QMC5883_CTRL_2,QMC5883_ROL_PNT)
        
    # set/reset period register
    def getSetResetPeriod(self):
        return self.readByte(QMC5883_SET_PERIOD)

    def setSetResetPeriod(self,value):
        self.writeByte(QMC5883_SET_PERIOD,value)
    
    def getMag16Bits(self):
        data = self.readBytes(QMC5883_DATA_X_LSB,6)
        mag_x = data[1] << 8 | data[0]
        mag_y = data[3] << 8 | data[2]
        mag_z = data[5] << 8 | data[4]
        return (mag_x,mag_y,mag_z)

    def getMagRaw(self):
        magRaw = [0]*3
        if self.getDataSkip():
            data = self.readBytes(QMC5883_DATA_X_LSB,6)
        # apply smoothing if smoothing value is set
        if self.debug:
            print("Averaging over {:d} measurements".format(self.smoothing))
        for _ in range(self.smoothing):
            # check data ready
            timeout = 0
            while not self.getDataReady() and timeout < 200:   # should not take longer than 200 ms
                timeout +=1
                sleep_ms(1)
            if timeout >= 200:
                raise Exception("Acquisition timeout")
            tmp = list(self.getMag16Bits())
            for axis in range(3):
                if tmp[axis] & 0x8000:
                    tmp[axis] -= 0x10000
                magRaw[axis] += tmp[axis]
        for axis in range(3):
            magRaw[axis] /= self.smoothing
            
        return tuple(magRaw)

    def getMagRaw_x(self):
        return self.getMagRaw()[X]

    def getMagRaw_y(self):
        return self.getMagRaw()[Y]

    def getMagRaw_Z(self):
        return self.getMagRaw()[Z]
        
    def getMag(self):
        # get the full range
        if self.getRange() == QMC5883_2G:
            fullRange = 2.0
        else:
            fullRange = 8.0
        rawData = self.getMagRaw()
        self.mag_x = rawData[X]*fullRange*1000/0x7fff
        self.mag_y = rawData[Y]*fullRange*1000/0x7fff
        self.mag_z = rawData[Z]*fullRange*1000/0x7fff
        if self.debug:
            print("mag_x: {:8.4f},mag_x: {:8.4f},mag_x: {:8.4f}".format(
                self.mag_x,self.mag_y,self.mag_z))
        return (self.mag_x,self.mag_y,self.mag_z)
    
    def getMag_x(self):
        return self.getMag()[X]

    def getMag_y(self):
        return self.getMag()[Y]

    def getMag_z(self):
        return self.getMag()[Z
                             ]      
    def getTempRaw(self):
        data = self.readBytes(QMC5883_TEMP_LSB,2)
        temp = data[1] << 8 | data[0]
        if temp > 0x7fff:
            temp -= 0x10000
        return temp

    def setTempOffset(self,value):
        # The temperature sensor only supplies relative values
        # In order to get absolute measurements the offset must be determined by a different sensor
        self.tempOffset = value

    def getTempOffset(self):
        return self.TempOffset
    
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
    
    def getHeading(self):
        if self.mag_x == None  or self.mag_y == None:
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

    # interrupts

    def drdyHandler(self,src):
        data = self.getMagRaw()
        print("mag_x: {:d}, mag_y: {:d}, mag_z: {:d}".format(data[0],data[1],data[2]))
        
    def enbleDrdyInt(self):
        self.drdy.irq(trigger=Pin.IRQ_RISING,handler=drdyHandler)

    def disableDrdyInt(self):
        self.drdy.irq(trigger=Pin.IRQ_RISING,handler=None)

    def setSmoothing(self,value):
        self.smoothing = value

    def getSmoothing(self):
        return self.smoothing
    
    def printRegValues(self):
        print("=============== register status =================")
        print("Status: 0x{:02x}".format(self.getStatus()))
        print("Status: data ready: ",self.getDataReady(),end=" ")
        print("Status: overflow: ",self.getOverflow(),end=" ")
        print("Status: Skipping data: ",self.getDataSkip())        
        print("Control register 1: 0x{:02x}".format(self.getCtrl_1()))
        print("Mode: ",QMC5883_MODE[self.getMode()],end=", ")
        print("Output rate: ",QMC5883_OUTPUT_RATE[self.getOutputRate()],end=", ")
        print("Full scale: ",QMC5883_RANGE[self.getRange()],end=", ")
        print("Oversampling: {:d}".format(QMC5883_OVER_SAMPLING[self.getOversampling()]))
        print("Control register 2: 0x{:02x}".format(self.getCtrl_2()))
        print("Interrupt enable: ",self.getIntEnable(), end=", ")
        print("Roll over: ",self.getRollOver())
        print("Set/Reset Period: 0x{:02x}".format(self.getSetResetPeriod()))
        print("ID: 0x{:02x}".format(self.getID()))
