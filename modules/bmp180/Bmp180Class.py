#
# This is the Python module implementing access to the bmp180 temperature and
# barometric pressure sensor
# copyright (c) U. Raich UCC, Nov.2017
# This program is part of the embedded systems course at the
# University of Cape Coast
# released under GPL
# updated to run under MicroPython, U. Raich, 12.3.2020


# read the calibration parameter from the register
#
#	Parameter  |  MSB    |  LSB    |  bit
# ------------|---------|---------|-----------
#		AC1    |  0xAA   | 0xAB    | 0 to 7
#		AC2    |  0xAC   | 0xAD    | 0 to 7
#		AC3    |  0xAE   | 0xAF    | 0 to 7
#		AC4    |  0xB0   | 0xB1    | 0 to 7
#		AC5    |  0xB2   | 0xB3    | 0 to 7
#		AC6    |  0xB4   | 0xB5    | 0 to 7
#		B1     |  0xB6   | 0xB7    | 0 to 7
#		B2     |  0xB8   | 0xB9    | 0 to 7
#		MB     |  0xBA   | 0xBB    | 0 to 7
#		MC     |  0xBC   | 0xBD    | 0 to 7
#		MD     |  0xBE   | 0xBF    | 0 to 7
#
from machine import I2C,Pin
from ustruct import unpack
import sys,time

BMP180_ADDRESS         = 0x77

#
# bmp180 power modes:
#
ULTRA_LOW_POWER       = 0
STANDARD_POWER        = 1
HIGH_RESOLUTION       = 2
ULTRA_HIGH_RESOLUTION = 3

BMP180_AC1_REG         =0xaa
BMP180_AC2_REG         =0xac
BMP180_AC3_REG         =0xae
BMP180_AC4_REG         =0xb0
BMP180_AC5_REG         =0xb2
BMP180_AC6_REG         =0xb4

BMP180_B1_REG          =0xb6
BMP180_B2_REG          =0xb8

BMP180_MB_REG          =0xba
BMP180_MC_REG          =0xbc
BMP180_MD_REG          =0xbe

BMP180_OUT_XLSB_REG    =0xf8
BMP180_OUT_LSB_REG     =0xf7
BMP180_OUT_MSB_REG     =0xf6

BMP180_CTRL_MEAS_REG   =0xf4

BMP180_SOFT_RESET      =0xe0
BMP180_CHIP_ID_REG     =0xd0

BMP180_CHIP_ID         =0x55
BMP180_MEAS_TEMP       =0x2e
BMP180_MEAS_PRESS      =0x34

I2C_BUS                =   1
SCL                    =  22
SDA                    =  21

class Bmp180:
    AC1 = -1
    AC2 = -1
    AC3 = -1
    AC4 = -1
    AC5 = -1
    AC6 = -1
    B1  = -1
    B2  = -1
    MB  = -1
    MC  = -1
    MD  = -1
    oversampling           = -1
    _samplingWait          = -1
    _samplingWaitTable     = []

    uncompensatedTemperature = -1
    uncompensatedPressure    = -1
    
    chip_id                 = -1
    temperature             = -1
    pressure                = -1
    debug                   = False
    
    def __init__(self):
                
        #
        # open the hardware I2C bus driver
        #
        if sys.platform == "esp8266":
            self.i2c =  I2C(scl=Pin(5), sda=Pin(4), freq=100000)   # on esp8266
        else:
            self.i2c = I2C(I2C_BUS,scl=Pin(SCL), sda=Pin(SDA), freq=400000)   # on esp32

        # check if we can find the bmp180
        devices = self.i2c.scan()
        found = False
        for i in range(len(devices)):
            if devices[i] == 0x77:
                found=True
                break
        if not found:
            print("No BMP180 found on the I2C bus, giving up ...")
            sys.exit(-1)
        # check if we find the right chip id    
        chip_id = unpack('B',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_CHIP_ID_REG, 1))[0]
        if chip_id != BMP180_CHIP_ID:
            print("This does not seem to be a BMP180 chip")
            sys.exit(-1)

#
# read calibration data
#
        self.AC1 = unpack('>h',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_AC1_REG, 2))[0]
        self.AC2 = unpack('>h',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_AC2_REG, 2))[0]
        self.AC3 = unpack('>h',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_AC3_REG, 2))[0]
#
# A4, A5, A6 are unsigned shorts
#
# all the other calibration values are signed shorts
#         
        self.AC4 = unpack('>H',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_AC4_REG, 2))[0]
        self.AC5 = unpack('>H',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_AC5_REG, 2))[0]
        self.AC6 = unpack('>H',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_AC6_REG, 2))[0]
        self.B1  = unpack('>h',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_B1_REG, 2))[0]
        self.B2  = unpack('>h',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_B2_REG, 2))[0]
        self.MB  = unpack('>h',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_MB_REG, 2))[0]
        self.MC  = unpack('>h',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_MC_REG, 2))[0]
        self.MD  = unpack('>h',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_MD_REG, 2))[0]
        
        self.oversampling       = ULTRA_HIGH_RESOLUTION
        self._samplingWaitTable = [5,8,14,26]        # waits in ms 
        self._samplingWait = self._samplingWaitTable[self.oversampling]
        return
        
#
# set the calibration values from the data sheet as well as their readout
# for uncompensated temperature and pressure to test the
# conversion algorithm
#
    def dummyCalib(self):
        self.AC1 =    408
        self.AC2 =    -72
        self.AC3 = -14383
        self.AC4 =  32741
        self.AC5 =  32757
        self.AC6 =  23153
        self.B1  =   6190
        self.B2  =      4
        self.MB  = -32768
        self.MC  =  -8711
        self.MD  =   2868
        self.uncompensatedTemperature = 27898
        self.uncompensatedPressure    = 23843
        self.oversampling = ULTRA_LOW_POWER

#
# set oversampling
#
    def setResolution(self,oss):

        if oss < 0 or oss > 3:
            printf("in setResolution: invalid oversampling code. Skipping...")
            return
        self.oversampling = oss
        self._samplingWait = self._samplingWaitTable[oss]
#
# read back oversampling code
#
    def getResolution(self):
            return self.oversampling    
#
# read the chip id
#
    def chipID(self):
        chip_id = unpack('B',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_CHIP_ID_REG, 1))[0]
        return chip_id       

#
# make a measurement
#

    def measure(self):
#
# start a temperature reading
#
        self.i2c.writeto_mem(BMP180_ADDRESS, BMP180_CTRL_MEAS_REG, bytearray([BMP180_MEAS_TEMP]))
        time.sleep_ms(5)      # wait 5 ms
        self.uncompensatedTemperature = unpack('>H',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_OUT_MSB_REG, 2))[0]

        if self.debug:
            print("in measure: uncompensated temperature: ",
                  self.uncompensatedTemperature)
#
# start a pressure reading
#
        cmd = BMP180_MEAS_PRESS + (self.oversampling << 6)
        if self.debug:
            print("Cmd to measure pressure: %x"%cmd)
            print("bytearray(cmd): ",bytearray([cmd]))

        self.i2c.writeto_mem(BMP180_ADDRESS, BMP180_CTRL_MEAS_REG, bytearray([cmd]))
        time.sleep_ms(self._samplingWait)
        
        self.MSB_raw  = unpack('B',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_OUT_MSB_REG, 1))[0]
        self.LSB_raw  = unpack('B',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_OUT_LSB_REG, 1))[0]
        self.XLSB_raw = unpack('B',self.i2c.readfrom_mem(BMP180_ADDRESS, BMP180_OUT_XLSB_REG, 1))[0]
        
        self.uncompensatedPressure = self.MSB_raw << 16 | self.LSB_raw << 8 | self.XLSB_raw
        self.uncompensatedPressure >>= (8-self.oversampling)
#        
        if self.debug:
            print("in measure: raw Pressure: %x %x %x"%(self.MSB_raw,self.LSB_raw,self.XLSB_raw))
            print("in measure: raw Pressure (combined): %x"%self.uncompensatedPressure)
            print("in measure: shift: %d"%(8-self.oversampling))
            print("in measure: uncompensated pressure: ", self.uncompensatedPressure)
        self.convert()
        
#
# calculate real temperature
#
    def convert(self):
        if self.debug:
            print("in convert: -------------- calibration values-- ------------")
            print("AC1: %d"%self.AC1)
            print("AC2: %d"%self.AC2)
            print("AC3: %d"%self.AC3)
            print("AC4: %d"%self.AC4)
            print("AC5: %d"%self.AC5)
            print("AC6: %d"%self.AC6)
            print("B1 : %d"%self.B1)
            print("B2 : %d"%self.B2)
            print("MB : %d"%self.MB)
            print("MC : %d"%self.MC)
            print("MD : %d"%self.MD)
            
        if self.debug:
            print("in convert: ------------ calculating temperature ------------")
        ut = self.uncompensatedTemperature
        if self.debug:        
            print("in convert: uncompensated temperature: ",ut)
            print("in convert: AC6: ",self.AC6," AC5: ",self.AC5)
        x1 = (ut - self.AC6) * self.AC5 >> 15
        if self.debug:
            print("in convert: x1:",x1)
        x2 = self.MC * 2048 // (x1+self.MD)
        if self.debug:
            print("in convert: x2:",x2)        
        b5 = x1 + x2
        if self.debug:
            print("in convert: b5:",b5)         
        t = (b5 + 8) >> 4
        if self.debug:
            print("in convert: calculated temperature: ",t)
        self.temperature = t/10       # in °C
#
# calculate pressure
#
        if self.debug:
            print("in convert: ------------ calculating pressure ------------")
        up = self.uncompensatedPressure
        b6 = b5 - 4000
        if self.debug:
            print("in convert: b6 =",b6)
        x1 = (self.B2 * (b6 * b6) >> 12) >> 11
        x2 = (self.AC2 * b6) >> 11
        x3 = x1 + x2    
        b3 = (((self.AC1 * 4 + x3) << self.oversampling) + 2) >> 2
        if self.debug:
            print("in convert: x1=" ,x1, " x2=",x2," x3=",x3," b3=" ,b3)
        x1 = self.AC3 * b6 >> 13
        x2 = (self.B1 * (b6 * b6) >> 12) >> 16
        x3 = ((x1 + x2) + 2) >> 2
        if self.debug:
            print("in convert: x1=" ,x1, " x2=",x2," x3=",x3)        
        b4 = self.AC4 * (x3 + 32768) >> 15
        if self.debug:
            print("in convert: b4=",b4)
        b7 = (up - b3) * (50000 >> self.oversampling)
        if self.debug:
            print("in convert: b7=",b7)
        if b7 < 0x80000000:
            p = (b7 * 2) // b4
        else:
            p = (b7//b4)*2
        if self.debug:
            print ("in convert: p=",p)
        x1 = (p>>8)*(p>>8)
        x1 = (x1*3038) >> 16
        x2 = (-7357 * p) >> 16
        if self.debug:
            print("in convert: x1=",x1," x2=",x2)
        p = p + ((x1 + x2 + 3791) >> 4)
        if self.debug:
            print("in convert: pressure:",p)
        self.pressure = p/100    # in hPa

#
# get temperature
#
    def getTemperature(self):
        return self.temperature

#
# get pressure
#
    def getPressure(self):
        return self.pressure
    
#
# set debugging on/off
#
    def setDebug(self,onOff):
        self.debug=onOff
        return
#
# read back calibration values
#
    def getCalib(self):
        return [self.AC1,self.AC2,self.AC3,self.AC4,self.AC5,self.AC6,self.B1,self.B2,self.MB,self.MC,self.MD]
