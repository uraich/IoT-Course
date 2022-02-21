# ADXL345: a class to drive the ADXL345 accelerometer
#

from machine import Pin,I2C
from micropython import const
from utime import sleep_ms

from adxl345_const import *

class ADXL345(object):
    
    def __init__(self,scl=22,sda=21,debug=False):
        self.debug = debug
        
        self.i2c = I2C(1,scl=Pin(scl),sda=Pin(sda),freq=400000)
        i2c_slaves = self.i2c.scan()
        if ADXL345_ADDRESS in i2c_slaves:
            if self.debug:
                print("ADXL345 I2C address found, continuing...")
        else:
            print("Cannot find ADXL345 address on the I2C bus")
            print("Please check your connections")
            return
        self.adxl345_addr = ADXL345_ADDRESS      
        devID = self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_DEVID,1)
        if self.debug:
            print("Device ID: 0x{:02x}".format(int(devID[0])))
        if int(devID[0]) != ADXL345_DEVICE_ID:
            print("Bad value from devid register, is the device a AXCL345?")
            return
        if self.debug :
            print("Found an ADXL345 on the I2C bus, continuing...")

    def setDebug(self,enable):
        self.debug = enable
        
    def bytesToInt(self,bytes):
        # the adxl345 return accelerometer data as signed 16 bit values
        # This routine combines the two bytes returned from the adxl345 for one axis and returns
        # converts it into a Python int value
        val = (bytes[0] << 8 ) | bytes[1]
        if self.debug:
            print("value: 0x{:04x}".format(val))
        if not val & 0x8000:           # positive 16 bit value
            if self.debug:
                print ("positive value: {:d}".format(val))
            return val
        else:
            val = -((val ^ 0xffff) + 1)
            if self.debug:
                print("negative value: {:d} ".format(val)) 
            return val

    def setBit(self,register,bit_pos,value):
        mask = 1 << bit_pos
        tmp = bytearray(1)
        tmp[0] = self.i2c.readfrom_mem(self.adxl345_addr,register,1)[0]
        if self.debug :
            print("Mask: 0x{:02x}, shift: {:d}".format(mask,bit_pos))
            print("Previous state of register 0x{:02x}: 0x{:02x}".format(register,tmp[0]))
        mask = ~mask # get rid of the previous state of the bit
        tmp[0] &= mask
        tmp[0] |= value << bit_pos
        if self.debug :
            print("New state of register 0x{:02x}: 0x{:02x}".format(register,tmp[0]))
        self.i2c.writeto_mem(self.adxl345_addr,register,tmp)
        
    def getBit(self,register,bit_pos):
        tmp = self.i2c.readfrom_mem(self.adxl345_addr,register,1)[0]
        if self.debug :
            print("read from register 0x{:02x}: 0x{:02x}".format(register,tmp))
        return (tmp >> bit_pos) & 1 

    def setBits(self,register,bitfield_pos,bitfield_size,value):
        tmp = bytearray(1)
        mask = 1
        for i in range(bitfield_size-1) :
            mask <<=1
            mask |=1
        shift = bitfield_pos - bitfield_size +1  
        mask <<= shift
        if self.debug:
            print("Mask: 0x{:02x}, shift: {:d}".format(mask,shift))
        tmp[0] = self.i2c.readfrom_mem(self.adxl345_addr,register,1)[0]
        if self.debug :
            print("Previous state of register 0x{:02x}: 0x{:02x}".format(register,tmp[0]))
             
        mask = ~mask # get rid of the previous state of the bit
        tmp[0] &= mask
        mask = ~mask
        tmp[0] |= value << shift & mask
        
        if self.debug :
            print("New state of register 0x{:02x}: 0x{:02x}".format(register,tmp[0]))
        
        self.i2c.writeto_mem(self.adxl345_addr,register,tmp)

    def getBits(self,register,bitfield_pos,bitfield_size):
        mask = 1
        for i in range(bitfield_size-1) :
            mask <<=1
            mask |=1
        shift = bitfield_pos -bitfield_size +1
        mask <<=shift
        if self.debug :
            print("mask = 0x{:02x}, shift = {:d}".format(mask,shift))
        tmp = self.i2c.readfrom_mem(self.adxl345_addr,register,1)[0]
        if self.debug :
            print("Value in register 0x{:02x}: 0x{:02x}".format(register,tmp))
        return (tmp & mask) >> shift
    
    def setTapThreshold(self,threshold) :
        tmp = bytearray(1)
        tmp[0] = threshold
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_THESH_TAP,tmp)

    def getTapThreshold(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_THESH_TAP,1)[0]
    
    def setXOffset(self,offset):
        tmp = bytearray(1)
        tmp[0] = offset
        if self.debug :
            print("Setting offset: 0x{:02x}".format(tmp[0]))
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_OFSX,tmp)

    def getXOffset(self):
        tmp =  self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_OFSX,1)[0]
        if tmp & 0x80 : # negative 8 bit number
            offset = int((~tmp+1) & 0xff)
            offset = -offset
        else :
            offset = int(tmp)
        if self.debug :
            print("Offset: ",offset)
        return offset
        
    def setYOffset(self,offset):
        tmp = bytearray(1)
        tmp[0] = offset
        if self.debug :
            print("Setting offset: 0x{:02x}".format(tmp[0]))
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_OFSY,tmp)

    def getYOffset(self):
        tmp =  self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_OFSY,1)[0]
        if tmp & 0x80 : # negative 8 bit number
            offset = int((~tmp+1) & 0xff)
            offset = -offset
        else :
            offset = int(tmp)
        if self.debug :
            print("Offset: ",offset)
        return offset
        
    def setZOffset(self,offset):
        tmp = bytearray(1)
        tmp[0] = offset
        if self.debug :
            print("Setting offset: 0x{:02x}".format(tmp[0]))
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_OFSZ,tmp)

    def getZOffset(self):
        tmp =  self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_OFSZ,1)[0]
        if tmp & 0x80 : # negative 8 bit number
            offset = int((~tmp+1) & 0xff)
            offset = -offset
        else :
            offset = int(tmp)
        if self.debug :
            print("Offset: ",offset)
        return offset
        
    def setTapDuration(self,duration):
        tmp = bytearray(1)
        tmp[0] = duration
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_DUR,tmp)

    def getTapDuration(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_DUR,1)[0]

    def setTapLatency(self,latency):
        tmp = bytearray(1)
        tmp[0] = latency
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_LATENT,tmp)

    def getTapLatency(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_LATENT,1)[0]
        
    def setTapWindow(self,timeWindow):
        tmp = bytearray(1)
        tmp[0] = timeWindow
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_WINDOW,tmp)

    def getTapWindow(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_WINDOW,1)[0]

    def setActivityThreshold(self,threshold):
        tmp = bytearray(1)
        tmp[0] = threshold
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_THRESH_ACT,tmp)

    def getActivityThreshold(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_THRESH_ACT,1)[0]

    def setInactivityThreshold(self,threshold):
        tmp = bytearray(1)
        tmp[0] = threshold
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_THRESH_INACT,tmp)

    def getActivityThreshold(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_THRESH_INACT,1)[0]

    def setInactivityTime(self,inactivityTime):
        tmp = bytearray(1)
        tmp[0] = inactivityTime
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_TIME_INACT,tmp)

    def getInactivityTime(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_TIME_INACT,1)[0]

    # ACT_INACT_CTL register
    def setAct_InactControl(self,act_inactControl):
        tmp = bytearray(1)
        tmp[0] = act_inactControl
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_ACT_INACT_CTL,tmp)

    def getAct_InactControl(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_ACT_INACT_CTL,1)[0]

    def setInactXEnable(self,en) :
        self.setBit(ADXL345_ACT_INACT_CTL,INACT_X_EN,en)

    def getInactXEnable(self):
        return self.getBit(ADXL345_ACT_INACT_CTL,INACT_X_EN)

    def setInactYEnable(self,en) :
        self.setBit(ADXL345_ACT_INACT_CTL,INACT_Y_EN,en)

    def getInactYEnable(self):
        return self.getBit(ADXL345_ACT_INACT_CTL,INACT_Y_EN)

    def setInactZEnable(self,en) :
        self.setBit(ADXL345_ACT_INACT_CTL,INACT_Z_EN,en)

    def getInactZEnable(self):
        return self.getBit(ADXL345_ACT_INACT_CTL,INACT_Z_EN)

    def setInactAC_DC(self,en) :
        self.setBit(ADXL345_ACT_INACT_CTL,INACT_AC_DC,en)

    def getInactAC_DC(self):
        return self.getBit(ADXL345_ACT_INACT_CTL,INACT_AC_DC)

    def setActXEnable(self,en) :
        self.setBit(ADXL345_ACT_INACT_CTL,ACT_X_EN,en)

    def getActXEnable(self):
        return self.getBit(ADXL345_ACT_ACT_CTL,ACT_X_EN)

    def setActYEnable(self,en) :
        self.setBit(ADXL345_ACT_INACT_CTL,ACT_Y_EN,en)

    def getActYEnable(self):
        return self.getBit(ADXL345_ACT_INACT_CTL,ACT_Y_EN)

    def setActZEnable(self,en) :
        self.setBit(ADXL345_ACT_INACT_CTL,ACT_Z_EN,en)

    def getActZEnable(self):
        return self.getBit(ADXL345_ACT_INACT_CTL,ACT_Z_EN)

    def setActAC_DC(self,en) :
        self.setBit(ADXL345_ACT_INACT_CTL,ACT_AC_DC,en)

    def getActZAC_DC(self):
        return self.getBit(ADXL345_ACT_INACT_CTL,ACT_AC_DC)
      
    def setFreeFallThreshold(self,threshold):
        tmp = bytearray(1)
        tmp[0] = threshold
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_THRESH_FF,tmp)

    def getFreeFallThreshold(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_THRESH_FF,1)[0]

    def setFreeFallTime(self,freeFallTime):
        tmp = bytearray(1)
        tmp[0] = freeFallTime
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_THRESH_FF,tmp)

    def getFreeFallTime(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_THRESH_FF,1)[0]

    # TAP_AXES register
    
    def setTapAxes(self,axis_enable):
        tmp = bytearray(1)
        tmp[0] = axis_enable
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_TAP_AXES,tmp)

    def getFreeFallTime(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_TAP_AXES,1)[0]

    def setTapXEnable(self,en) :
        self.setBit(ADXL345_TAP_AXES,TAP_X_EN,en)

    def getTapXEnable(self):
        return self.getBit(ADXL345_TAP_AXES,TAP_X_EN)
      
    def setTapYEnable(self,en) :
        self.setBit(ADXL345_TAP_AXES,TAP_Y_EN,en)

    def getTapYEnable(self):
        return self.getBit(ADXL345_TAP_AXES,TAP_Y_EN)
      
    def setTapZEnable(self,en) :
        self.setBit(ADXL345_TAP_AXES,TAP_Z_EN,en)

    def getTapZEnable(self):
        return self.getBit(ADXL345_TAP_AXES,TAP_Z_EN)

    def setTapSuppress(self,en) :
        self.setBit(ADXL345_TAP_AXES,SUPPRESS,en)

    def getTapSuppress(self):
        return self.getBit(ADXL345_TAP_AXES,SUPPRESS)
      
    # ACT_TAP_STATUS
    def getTapStatus(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_ACT_TAP_STATUS,1)[0]

    def getTapXSource(self):
        return self.getBit(ADXL345_ACT_TAP_STATUS,TAP_X_SOURCE)
    
    def getTapYSource(self):
        return self.getBit(ADXL345_ACT_TAP_STATUS,TAP_Y_SOURCE)
    
    def getTapZSource(self):
        return self.getBit(ADXL345_ACT_TAP_STATUS,TAP_Z_SOURCE)
    
    def getASleep(self):
        self.getBit(ADXL345_ACT_TAP_STATUS,ASLEEP)
    
    def getACTXSource(self):
        return self.getBit(ADXL345_ACT_TAP_STATUS,ACT_X_SOURCE)
    
    def getActYSource(self):
        return self.getBit(ADXL345_ACT_TAP_STATUS,ACT_Y_SOURCE)
    
    def getACtZSource(self):
        return self.getBit(ADXL345_ACT_TAP_STATUS,ACT_Z_SOURCE)
    
    # BW_RATE register
    def setDataRateAndPowerCtl(self,dataRateAndPowerCtl):
        tmp = bytearray(1)
        tmp[0] = dataRateAndPowerCtl
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_BW_RATE,tmp)

    def getDataRateAndPowerCtl(self) :
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_BW_RATE,1)[0]

    def setDataRate(self,dataRate):
        self.setBits(ADXL345_BW_RATE,RATE,RATE_SIZE,dataRate)

    def getDataRate(self) :
        return self.getBits(ADXL345_BW_RATE,RATE,RATE_SIZE)

    def setLowPower(self,lowPower) :    
        self.setBits(ADXL345_BW_RATE,LOW_POWER,LOW_POWER_SIZE,lowPower)
        
    def getLowPower(self) :
        return self.getBits(ADXL345_BW_RATE,LOW_POWER,LOW_POWER_SIZE)

    # POWER_CTL register
    def setPowerCtl(self,powerCtl):
        tmp = bytearray(1)
        tmp[0] = powerCtl
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_POWER_CTL,tmp)

    def getPowerCtl(self) :
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_POWER_CTL,1)[0]

    def setWakeUp(self,wakeup) :
        self.setBits(ADXL345_POWER_CTL,WAKEUP,WAKEUP_SIZE,wakeup)

    def getWakeUp(self) :
        return self.getBits(ADXL345_POWER_CTL,WAKEUP,WAKEUP_SIZE)

    def setSleep(self,sleepBit) :
        self.setBit(ADXL345_POWER_CTL,SLEEP,sleepBit)

    def getSleep(self) :
        return self.getBits(ADXL345_POWER_CTL,SLEEP)

    def setMeasure(self,measureBit) :
        self.setBit(ADXL345_POWER_CTL,MEASURE,measureBit)

    def getMEASURE(self) :
        return self.getBit(ADXL345_POWER_CTL,MEASURE)

    def setAutoSleep(self,autosleep) :
        self.setBits(ADXL345_POWER_CTL,AUTO_SLEEP,AUTO_SLEEP_SIZE,autosleep)

    def getAutoSleep(self) :
        return self.getBits(ADXL345_POWER_CTL,AUTO_SLEEP,AUTO_SIZE)

    def setLink(self,linkBit) :
        self.setBit(ADXL345_POWER_CTL,LINK,linkBit)

    def getLink(self) :
        return self.getBits(ADXL345_POWER_CTL,LINK)


    # INT_ENABLE register

    def setInterruptEnable(self,enable):
        tmp = bytearray(1)
        tmp[0] = enable
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_INT_ENABLE,tmp)

    def getInterruptEnable(self) :
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_INT_ENABLE,1)[0]

    def setOverrunIntEnable(self,enable) :
        self.setBit(ADXL345_INT_ENABLE,OVERRUN,enable)

    def getOverrunIntEnable(self) :
        return self.getBits(ADXL345_INT_ENABLE,OVERRUN)

    def setWatermarkIntEnable(self,enable) :
        self.setBit(ADXL345_INT_ENABLE,WATERMARK,enable)

    def getWatermarkIntEnable(self) :
        return self.getBits(ADXL345_INT_ENABLE,WATERMARK)

    def setFreeFallIntEnable(self,enable) :
        self.setBit(ADXL345_INT_ENABLE,FREE_FALL,enable)

    def getFreeFallIntEnable(self) :
        return self.getBits(ADXL345_INT_ENABLE,FREE_FALL)

    def setInactivityIntEnable(self,enable) :
        self.setBit(ADXL345_INT_ENABLE,INACTIVITY,enable)

    def getInactivityIntEnable(self) :
        return self.getBits(ADXL345_INT_ENABLE,INACTIVITY)

    def setActivityIntEnable(self,enable) :
        self.setBit(ADXL345_INT_ENABLE,ACTIVITY,enable)

    def getActivityIntEnable(self) :
        return self.getBits(ADXL345_INT_ENABLE,ACTIVITY)

    def setDoubleTapIntEnable(self,enable) :
        self.setBit(ADXL345_INT_ENABLE,DOUBLE_TAP,enable)

    def getDoubleTapIntEnable(self) :
        return self.getBits(ADXL345_INT_ENABLE,DOUBLE_TAP)

    def setSingleTapIntEnable(self,enable) :
        self.setBit(ADXL345_INT_ENABLE,SINGLE_TAP,enable)

    def getSingleTapIntEnable(self) :
        return self.getBits(ADXL345_INT_ENABLE,SINGLE_TAP)

    def setDataReadyIntEnable(self,enable) :
        self.setBit(ADXL345_INT_ENABLE,DATA_READY,enable)

    def getDataReadyIntEnable(self) :
        return self.getBits(ADXL345_INT_ENABLE,DATA_READY)

    # INT_MAP register

    def setInterruptMapping(self,enable):
        tmp = bytearray(1)
        tmp[0] = enable
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_INT_MAP,tmp)

    def getInterruptMapping(self) :
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_INT_MAP,1)[0]

    def setOverrunMapping(self,enable) :
        self.setBit(ADXL345_INT_MAP,OVERRUN,enable)

    def getOverrunMapping(self) :
        return self.getBits(ADXL345_INT_MAP,OVERRUN)

    def setWatermarkMapping(self,enable) :
        self.setBit(ADXL345_INT_MAP,WATERMARK,enable)

    def getWatermarkMapping(self) :
        return self.getBits(ADXL345_INT_MAP,WATERMARK)

    def setFreeFallMapping(self,enable) :
        self.setBit(ADXL345_INT_MAP,FREE_FALL,enable)

    def getFreeFallMapping(self) :
        return self.getBits(ADXL345_INT_MAP,FREE_FALL)

    def setInactivityMapping(self,enable) :
        self.setBit(ADXL345_INT_MAP,INACTIVITY,enable)

    def getInactivityMapping(self) :
        return self.getBits(ADXL345_INT_MAP,INACTIVITY)

    def setActivityMapping(self,enable) :
        self.setBit(ADXL345_INT_MAP,ACTIVITY,enable)

    def getActivityMapping(self) :
        return self.getBits(ADXL345_INT_MAP,ACTIVITY)

    def setDoubleTapMapping(self,enable) :
        self.setBit(ADXL345_INT_MAP,DOUBLE_TAP,enable)

    def getDoubleTapMapping(self) :
        return self.getBits(ADXL345_INT_MAP,DOUBLE_TAP)

    def setSingleTapMapping(self,enable) :
        self.setBit(ADXL345_INT_MAP,SINGLE_TAP,enable)

    def getSingleTapMapping(self) :
        return self.getBits(ADXL345_INT_MAP,SINGLE_TAP)

    def setDataReadyMapping(self,enable) :
        self.setBit(ADXL345_INT_MAP,DATA_READY,enable)

    def getDataReadyMapping(self) :
        return self.getBits(ADXL345_INT_MAP,DATA_READY)

    # INT_SOURCE register

    def getInterruptSource(self) :
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_INT_SOURCE,1)[0]

    def getOverrunSource(self) :
        return self.getBit(ADXL345_INT_SOURCE,OVERRUN)

    def getWatermarkSource(self) :
        return self.getBit(ADXL345_INT_SOURCE,WATERMARK)

    def getFreeFallSource(self) :
        return self.getBit(ADXL345_INT_SOURCE,FREE_FALL)

    def getInactivitySource(self) :
        return self.getBit(ADXL345_INT_SOURCE,INACTIVITY)

    def getActivitySource(self) :
        return self.getBit(ADXL345_INT_SOURCE,ACTIVITY)

    def getDoubleTapSource(self) :
        return self.getBit(ADXL345_INT_SOURCE,DOUBLE_TAP)

    def getSingleTapSource(self) :
        return self.getBit(ADXL345_INT_SOURCE,SINGLE_TAP)

    def getDataReady(self) :
        return self.getBit(ADXL345_INT_SOURCE,DATA_READY)

    # DATA_FORMAT register
    def setDataFormat(self,format):
        tmp = bytearray(1)
        tmp[0] = format
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_DATA_FORMAT,tmp)

    def getDataFormat(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_DATA_FORMAT,1)[0]

    def setRange(self,range) :
        self.setBits(ADXL345_DATA_FORMAT,RANGE,RANGE_SIZE,range)

    def getRange(self) :
        return self.getBits(ADXL345_DATA_FORMAT,RANGE,RANGE_SIZE)

    def setJustiy(self,justify) :
        self.setBit(ADXL345_DATA_FORMAT,JUSTIFY,justify)

    def getJustify(self) :
        return self.getBits(ADXL345_DATA_FORMAT,JUSTIFY)
    
    def setFullRes(self,fullres) :
        self.setBit(ADXL345_DATA_FORMAT,FULL_RES,fullres)

    def getFullRes(self) :
        return self.getBits(ADXL345_DATA_FORMAT,FULL_RES)
    
    def setInterruptInvert(self,intInvert) :
        self.setBit(ADXL345_DATA_FORMAT,INT_,intInvert)

    def getInterruptInvert(self) :
        return self.getBits(ADXL345_DATA_FORMAT,INT_INVERT)
    
    def setSPIMode(self,spiMode) :
        self.setBit(ADXL345_DATA_FORMAT,SPI,spiMode)

    def getSPIMode(self) :
        return self.getBits(ADXL345_DATA_FORMAT,SPI)
    
    def setSelfTest(self,selfTest) :
        self.setBit(ADXL345_DATA_FORMAT,SELF_TEST,selfTest)

    def getSelfTest(self) :
        return self.getBits(ADXL345_DATA_FORMAT,SELF_TEST)
    

    # FIFO_CTL register
    def setFIFO_Ctl(self,fifoControl):
        tmp = bytearray(1)
        tmp[0] = fifoControl
        self.i2c.writeto_mem(self.adxl345_addr,ADXL345_FIFO_CTL,tmp)

    def getFIFO_Ctl(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_FIFO_CTL,1)[0]

    def setSamples(self,samples) :
        self.setBits(ADXL345_FIFO_CTL,SAMPLES,SAMPLES_SIZE,samples)

    def getSamples(self) :
        return self.getBits(ADXL345_FOF_CTL,SAMPLES,SAMPLES_SIZE)

    def setTrigger(self,trigger) :
        self.setBit(ADXL345_FIFO_CTL,TRIGGER,trigger)

    def getTrigget(self) :
        return self.getBits(ADXL345_FIFO_CTL,TRIGGER)

    def setFiFoMode(self,fifoMode) :
        self.setBits(ADXL345_FIFO_CTL,FIFO_TYPE,FIFO_TYPE_SIZE,fifoMode)

    def getFiFoMode(self) :
        return self.getBits(ADXL345_FOF_CTL,FIFO_TYPE,FIFO_TYPE_SIZE)

    # FIFO_STATUS
    def getFIFO_Status(self):
        return self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_FIFO_STATUS,1)[0]

    def getFIFO_Entries(self):
        return self.getBits(ADXL345_FIFO_STATUS,FIFO_ENTRIES,FIFO_ENTRIES_SIZE)

    def getFIFO_Trigger():
        return self.getBit(ADXL345_FIFO_STATUS,FIFO_TRIG)
    
    # Accelerometer data registers
    def getAccelerometerData(self) :
        tmp = self.i2c.readfrom_mem(self.adxl345_addr,ADXL345_DATAAX0,6)
        raw = bytearray(2)
        raw[0] = tmp[1]
        raw[1] = tmp[0]
        ax = self.bytesToInt(raw)
        raw[0] = tmp[3]
        raw[1] = tmp[2]
        ay = self.bytesToInt(raw)
        raw[0] = tmp[5]
        raw[1] = tmp[4]
        az = self.bytesToInt(raw)
        return(ax,ay,az)
