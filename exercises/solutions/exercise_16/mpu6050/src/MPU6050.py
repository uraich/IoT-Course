'''! 
I2Cdev library collection - MPU6050 I2C device class
Based on InvenSense MPU-6050 register map document rev. 2.0, 5/19/2011 (RM-MPU-6000A-00)
8/24/2011 by Jeff Rowberg <jeff@rowberg.net>
Updates should (hopefully) always be available at https://github.com/jrowberg/i2cdevlib

Changelog:
 2022-02-02 - ported to MicroPython by U. Raich
 2021-09-27 - split implementations out of header files, finally
 2019-07-08 - Added Auto Calibration routine
    ... - ongoing debug release

NOTE: THIS IS ONLY A PARIAL RELEASE. THIS DEVICE CLASS IS CURRENTLY UNDERGOING ACTIVE
DEVELOPMENT AND IS STILL MISSING SOME IMPORTANT FEATURES. PLEASE KEEP THIS IN MIND IF
YOU DECIDE TO USE THIS PARTICULAR CODE FOR ANYTHING.

'''
'''
============================================
I2Cdev device library code is placed under the MIT license
Copyright (c) 2012 Jeff Rowberg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================
'''

from machine import Pin,I2C,SoftI2C
from struct import pack
from MPU6050_const import *
from time import sleep_ms, sleep_us, time

class MPU6050:
    
    def __init__(self,address=MPU6050_ADDRESS_AD0_LOW,bus=1,scl=22,sda=21,debug=False):

        '''
        Power on and prepare for general usage.
        This will activate the device and take it out of sleep mode (which must be done
        after start-up). This function also sets both the accelerometer and the gyroscope
        to their most sensitive settings, namely +/- 2g and +/- 250 degrees/sec, and sets
        the clock source to use the X Gyro for reference, which is slightly better than
        the default internal clock source.
        '''
        self.mpu6050_address = address
            
        self.debug=debug                         # default: no debugging print-outs

        if self.debug:
            print("I2C address of MPU6050: 0x{:02x}".format(self.mpu6050_address))
            
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
        # Check if an MPU6050 is connected to the I2C bus
        try:
            i2c_slaves = self.i2c.scan()
        except:
            raise Exception("MPU6050: Cannot access the I2C bus")
        
        self.fifoTimeout = 0
        
        # Check if there is an MPU6050 on the I2C bus
        if self.mpu6050_address not in i2c_slaves:
            raise Exception("No MPU6050 found on I2C bus. Please connect the module first.")
        self.setClockSource(MPU6050_CLOCK_PLL_XGYRO)
        self.setFullScaleGyroRange(MPU6050_GYRO_FS_250)
        self.setFullScaleAccelRange(MPU6050_ACCEL_FS_2)
        self.setSleepEnabled(False) # thanks to Jack Elston for pointing this one out!

    def setDebug(self,onOff):
        '''!
        set the debugging flag
        @param onOff: sets the debug flag
        '''
        self.debug = onOff
        
    def readBits(self, register, bit_position, no_of_bits):
        '''!
        Reads a number of bits from the register
        @param bit_position: the left most position of the bit field
        @param no_of_bits: the number of bits in the bit field
        '''
        tmp = self.i2c.readfrom_mem(self.mpu6050_address,register,1)[0]
        # print("Who am I register unshifted raw: 0x{:02x}".format(tmp))
        mask = 1
        for i in range(1,no_of_bits):
            mask = mask << 1 | 1
        shift = bit_position - no_of_bits + 1
        mask <<= shift        
        # print("mask: 0x{:02x}".format(mask))
        tmp &= mask
        return tmp >> shift

    def readBit(self,register,bit_position) :
        '''!
        Reads a single bit from the register
        @param register: reguster address from which the bit is read
        @param bit_position: the left most position of the bit field
        '''
        tmp = self.i2c.readfrom_mem(self.mpu6050_address,register,1)[0]
        if tmp & (1 << bit_position) :
            return True
        else:
            return False
        
    def writeBits(self, register, bit_position, no_of_bits, value):
        '''!
        Writes a number of bits to the register
        @param bit_position: the left most position of the bit field
        @param no_of_bits: the number of bits in the bit field
        @param value: the value to be written
        '''        
        tmp = bytearray(self.i2c.readfrom_mem(self.mpu6050_address,register,1))
        if self.debug:
            print("Register 0x{:02x} raw: 0x{:02x}".format(register,tmp[0]))
        mask = 1
        for i in range(1,no_of_bits):
            mask = mask << 1 | 1
        shift = bit_position - no_of_bits + 1
        mask <<= shift        
        # print("mask: 0x{:02x}".format(mask))
        mask = ~ mask
        tmp[0] &= mask
        tmp[0] |= value <<shift
        if self.debug:
            print("Writing 0x{:02x} to register 0x{:02x}".format(tmp[0],register))
        self.i2c.writeto_mem(self.mpu6050_address,register,tmp)

    def writeBit(self,register,bit_position,value):
        '''!
        Writes single bit to the register
        @param bit_position: the left most position of the bit field
        @param no_of_bits: the number of bits in the bit field
        @param value: the value to be written
        '''               
        tmp = bytearray(self.i2c.readfrom_mem(self.mpu6050_address,register,1))
        if self.debug:
            print("writeBit: Original content of register 0x{:02x} : 0x{:02x}".format(register,tmp[0]))
        if value:
            tmp[0] |= (1 << bit_position)
        else:
            tmp[0] &= ~(1 << bit_position)
        if self.debug:
            print("writeBit: New content of register 0x{:02x} : 0x{:02x}".format(register,tmp[0]))
        self.i2c.writeto_mem(self.mpu6050_address,register,tmp)
        
    # WHO_AM_I register
    def getDeviceID(self) :
        '''!
        Get Device ID.
        This register is used to verify the identity of the device (0b110100, 0x34).
        @return Device ID (6 bits only! should be 0x34)
        @see MPU6050_RA_WHO_AM_I
        @see MPU6050_WHO_AM_I_BIT
        @see MPU6050_WHO_AM_I_LENGTH
        '''

        tmp = self.readBits(MPU6050_RA_WHO_AM_I, MPU6050_WHO_AM_I_BIT, MPU6050_WHO_AM_I_LENGTH)
        # print("Who am I = 0x{:02x}".format(tmp))
        return tmp
    
    def testConnection(self) :
        '''!
        Verify the I2C connection.
         Make sure the device is connected and responds as expected.
         @return True if connection is valid, false otherwise
         '''
        return self.getDeviceID() == 0x34

    def setClockSource(self,source) :
        '''!
        Set clock source setting.
        An internal 8MHz oscillator, gyroscope based clock, or external sources can
        be selected as the MPU-60X0 clock source. When the internal 8 MHz oscillator
        or an external source is chosen as the clock source, the MPU-60X0 can operate
        in low power modes with the gyroscopes disabled.
        
        Upon power up, the MPU-60X0 clock source defaults to the internal oscillator.
        However, it is highly recommended that the device be configured to use one of
        the gyroscopes (or an external clock source) as the clock reference for
        improved stability. The clock source can be selected according to the following table:
 
        <pre>
        CLK_SEL | Clock Source
        --------+--------------------------------------
        0       | Internal oscillator
        1       | PLL with X Gyro reference
        2       | PLL with Y Gyro reference
        3       | PLL with Z Gyro reference
        4       | PLL with external 32.768kHz reference
        5       | PLL with external 19.2MHz reference
        6       | Reserved
        7       | Stops the clock and keeps the timing generator in reset
        </pre>
 
        @param source New clock source setting
        @see getClockSource()
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_CLKSEL_BIT
        @see MPU6050_PWR1_CLKSEL_LENGTH
        '''
        self.writeBits(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CLKSEL_BIT, MPU6050_PWR1_CLKSEL_LENGTH, source)
        
    def getClockSource(self) :
        '''!
        Get clock source setting.
        @return Current clock source setting
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_CLKSEL_BIT
        @see MPU6050_PWR1_CLKSEL_LENGTH
        '''
        return self.readBits(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CLKSEL_BIT, MPU6050_PWR1_CLKSEL_LENGTH)

    # GYRO_CONFIG register
    def getFullScaleGyroRange(self) :
        '''!
        Get full-scale gyroscope range.
        The FS_SEL parameter allows setting the full-scale range of the gyro sensors,
        as described in the table below.
        
        <pre>
        0 = +/- 250 degrees/sec
        1 = +/- 500 degrees/sec
        2 = +/- 1000 degrees/sec
        3 = +/- 2000 degrees/sec
        </pre>
        
        @return Current full-scale gyroscope range setting
        @see MPU6050_GYRO_FS_250
        @see MPU6050_RA_GYRO_CONFIG
        @see MPU6050_GCONFIG_FS_SEL_BIT
        @see MPU6050_GCONFIG_FS_SEL_LENGTH
        '''
        return self.readBits(MPU6050_RA_GYRO_CONFIG, MPU6050_GCONFIG_FS_SEL_BIT, MPU6050_GCONFIG_FS_SEL_LENGTH)

    def setFullScaleGyroRange(self,range):
        '''!
        Set full-scale gyroscope range.
        @param range New full-scale gyroscope range value
        @see getFullScaleRange()
        @see MPU6050_GYRO_FS_250
        @see MPU6050_RA_GYRO_CONFIG
        @see MPU6050_GCONFIG_FS_SEL_BIT
        @see MPU6050_GCONFIG_FS_SEL_LENGTH
        '''
        self.writeBits(MPU6050_RA_GYRO_CONFIG, MPU6050_GCONFIG_FS_SEL_BIT, MPU6050_GCONFIG_FS_SEL_LENGTH, range)

    # ACCEL_CONFIG register

    def getAccelConfig(self):
        '''!
        Read the accelerometer configuration register
        @return contents of the accel config register
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_CONFIG,1)[0]
                                     
    def setAccelConfig(self,config):
        '''!
        Write the accelerometer configuration register
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        tmp = bytearray(1)
        tmp[0] = config
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_ACCEL_CONFIG,tmp)
                                                                          
    def getAccelXSelfTest(self) :
        '''!
        Get self-test enabled setting for accelerometer X axis.
        @return Self-test enabled value
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        return self.readBit(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_XA_ST_BIT)

    def setAccelXSelfTest(self,enabled) :
        '''!
        Get self-test enabled setting for accelerometer X axis.
        @param enabled Self-test enabled value
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        self.writeBit(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_XA_ST_BIT, enabled)

    def getAccelYSelfTest(self) :
        '''!
        Get self-test enabled value for accelerometer Y axis.
        @return Self-test enabled value
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        return self.readBit(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_YA_ST_BIT)
        
    def setAccelYSelfTest(self,enabled) :
        '''!
        Get self-test enabled value for accelerometer Y axis.
        @param enabled Self-test enabled value
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        return self.writeBit(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_YA_ST_BIT, enabled)

    def getAccelZSelfTest(self) :
        '''!
        Get self-test enabled value for accelerometer Z axis.
        @return Self-test enabled value
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        return self.readBit(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_ZA_ST_BIT)

    def setAccelZSelfTest(self,enabled) :
        '''!
        Set self-test enabled value for accelerometer Z axis.
        @param enabled Self-test enabled value
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        self.writeBit(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_ZA_ST_BIT, enabled)

    def getFullScaleAccelRange(self) :
        '''!
        Get full-scale accelerometer range.
        The FS_SEL parameter allows setting the full-scale range of the accelerometer
        sensors, as described in the table below.

        <pre>
        0 = +/- 2g
        1 = +/- 4g
        2 = +/- 8g
        3 = +/- 16g
        </pre>
 
        @return Current full-scale accelerometer range setting
        @see MPU6050_ACCEL_FS_2
        @see MPU6050_RA_ACCEL_CONFIG
        @see MPU6050_ACONFIG_AFS_SEL_BIT
        @see MPU6050_ACONFIG_AFS_SEL_LENGTH
        '''

        return self.readBits(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_AFS_SEL_BIT, MPU6050_ACONFIG_AFS_SEL_LENGTH)

    def setFullScaleAccelRange(self,range) : # Set full-scale accelerometer range.
        '''!
        @param range New full-scale accelerometer range setting
        @see getFullScaleAccelRange()
        '''
        self.writeBits(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_AFS_SEL_BIT, MPU6050_ACONFIG_AFS_SEL_LENGTH, range)

    def getDHPFMode(self) :
        '''!
        Get the high-pass filter configuration.
        The DHPF is a filter module in the path leading to motion detectors (Free
        Fall, Motion threshold, and Zero Motion). The high pass filter output is not
        available to the data registers (see Figure in Section 8 of the MPU-6000/
        MPU-6050 Product Specification document).

        The high pass filter has three modes:

        <pre>
           Reset: The filter output settles to zero within one sample. This
                  effectively disables the high pass filter. This mode may be toggled
                  to quickly settle the filter.

           On:    The high pass filter will pass signals above the cut off frequency.

           Hold:  When triggered, the filter holds the present sample. The filter
                  output will be the difference between the input sample and the held
                  sample.
        </pre>

        <pre>
        ACCEL_HPF | Filter Mode | Cut-off Frequency
        ----------+-------------+------------------
        0         | Reset       | None
        1         | On          | 5Hz
        2         | On          | 2.5Hz
        3         | On          | 1.25Hz
        4         | On          | 0.63Hz
        7         | Hold        | None
        </pre>

        @return Current high-pass filter configuration
        @see MPU6050_DHPF_RESET
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        return self.readBits(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_ACCEL_HPF_BIT, MPU6050_ACONFIG_ACCEL_HPF_LENGTH)

    def setDHPFMode(self,bandwidth) :
        '''!
        Set the high-pass filter configuration.
        @param bandwidth New high-pass filter configuration
        @see setDHPFMode()
        @see MPU6050_DHPF_RESET
        @see MPU6050_RA_ACCEL_CONFIG
        '''
        self.writeBits(MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_ACCEL_HPF_BIT, MPU6050_ACONFIG_ACCEL_HPF_LENGTH, bandwidth)


    def setSleepEnabled(self,enabled) :
        '''!
        Set sleep mode status.
        @param enabled New sleep mode enabled status
        @see getSleepEnabled()
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_SLEEP_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_SLEEP_BIT, enabled)

    # AUX_VDDIO register (InvenSense demo code calls this RA_*G_OFFS_TC)
    
    def getAuxVDDIOLevel(self) :
        '''!
        Get the auxiliary I2C supply voltage level.
        When set to 1, the auxiliary I2C bus high logic level is VDD. When cleared to
        0, the auxiliary I2C bus high logic level is VLOGIC. This does not apply to
        the MPU-6000, which does not have a VLOGIC pin.
        @return I2C supply voltage level (0=VLOGIC, 1=VDD)
        '''
        return readBit(MPU6050_RA_YG_OFFS_TC, MPU6050_TC_PWR_MODE_BIT)

    def setAuxVDDIOLevel(self,level) :
        '''!
        Set the auxiliary I2C supply voltage level.
        When set to 1, the auxiliary I2C bus high logic level is VDD. When cleared to
        0, the auxiliary I2C bus high logic level is VLOGIC. This does not apply to
        the MPU-6000, which does not have a VLOGIC pin.
        @param level I2C supply voltage level (0=VLOGIC, 1=VDD)
        '''
        writeBit(MPU6050_RA_YG_OFFS_TC, MPU6050_TC_PWR_MODE_BIT, level)
        
    # SMPLRT_DIV register

    def getRate(self) :
        '''!
        Get gyroscope output rate divider.
        The sensor register output, FIFO output, DMP sampling, Motion detection, Zero
        Motion detection, and Free Fall detection are all based on the Sample Rate.
        The Sample Rate is generated by dividing the gyroscope output rate by
        SMPLRT_DIV:

        Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV)

        where Gyroscope Output Rate = 8kHz when the DLPF is disabled (DLPF_CFG = 0 or
        7), and 1kHz when the DLPF is enabled (see Register 26).
 
        Note: The accelerometer output rate is 1kHz. This means that for a Sample
        Rate greater than 1kHz, the same accelerometer sample may be output to the
        FIFO, DMP, and sensor registers more than once.
        
        For a diagram of the gyroscope and accelerometer signal paths, see Section 8
        of the MPU-6000/MPU-6050 Product Specification document.
 
        @return Current sample rate
        @see MPU6050_RA_SMPLRT_DIV
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_SMPLRT_DIV,1)[0]

    def setRate(self,rate) :
        '''!
        Set gyroscope sample rate divider.
        @param rate New sample rate divider
        @see getRate()
        @see MPU6050_RA_SMPLRT_DIV
        '''
        tmp = bytearray(1)
        tmp[0] = rate
        self.i2c.writeto_mem(self.mpu6050_address,register,tmp)

    # CONFIG register
    
    def getExternalFrameSync(self) :
        '''!
        Get external FSYNC configuration.
        Configures the external Frame Synchronization (FSYNC) pin sampling. An
        external signal connected to the FSYNC pin can be sampled by configuring
        EXT_SYNC_SET. Signal changes to the FSYNC pin are latched so that short
        strobes may be captured. The latched FSYNC signal will be sampled at the
        Sampling Rate, as defined in register 25. After sampling, the latch will
        reset to the current FSYNC signal state.
 
        The sampled value will be reported in place of the least significant bit in
        a sensor data register determined by the value of EXT_SYNC_SET according to
        the following table.
 
        <pre>
        EXT_SYNC_SET | FSYNC Bit Location
        -------------+-------------------
        0            | Input disabled
        1            | TEMP_OUT_L[0]
        2            | GYRO_XOUT_L[0]
        3            | GYRO_YOUT_L[0]
        4            | GYRO_ZOUT_L[0]
        5            | ACCEL_XOUT_L[0]
        6            | ACCEL_YOUT_L[0]
        7            | ACCEL_ZOUT_L[0]
        </pre>
 
        @return FSYNC configuration value
        '''
        return self.readBits(MPU6050_RA_CONFIG, MPU6050_CFG_EXT_SYNC_SET_BIT, MPU6050_CFG_EXT_SYNC_SET_LENGTH)

    def setExternalFrameSync(self,sync) :
        '''!
        Set external FSYNC configuration.
        @see getExternalFrameSync()
        @see MPU6050_RA_CONFIG
        @param sync New FSYNC configuration value
        '''
        writeBits(MPU6050_RA_CONFIG, MPU6050_CFG_EXT_SYNC_SET_BIT, MPU6050_CFG_EXT_SYNC_SET_LENGTH, sync)

    def getDLPFMode(self) :
        '''!
        Get digital low-pass filter configuration.
        The DLPF_CFG parameter sets the digital low pass filter configuration. It
        also determines the internal sampling rate used by the device as shown in
        the table below.
 
        Note: The accelerometer output rate is 1kHz. This means that for a Sample
        Rate greater than 1kHz, the same accelerometer sample may be output to the
        FIFO, DMP, and sensor registers more than once.
        
        <pre>
          |   ACCELEROMETER    |           GYROSCOPE
        DLPF_CFG | Bandwidth | Delay  | Bandwidth | Delay  | Sample Rate
        ---------+-----------+--------+-----------+--------+-------------
        0        | 260Hz     | 0ms    | 256Hz     | 0.98ms | 8kHz
        1        | 184Hz     | 2.0ms  | 188Hz     | 1.9ms  | 1kHz
        2        | 94Hz      | 3.0ms  | 98Hz      | 2.8ms  | 1kHz
        3        | 44Hz      | 4.9ms  | 42Hz      | 4.8ms  | 1kHz
        4        | 21Hz      | 8.5ms  | 20Hz      | 8.3ms  | 1kHz
        5        | 10Hz      | 13.8ms | 10Hz      | 13.4ms | 1kHz
        6        | 5Hz       | 19.0ms | 5Hz       | 18.6ms | 1kHz
        7        |   -- Reserved --   |   -- Reserved --   | Reserved
        </pre>
 
        @return DLFP configuration
        @see MPU6050_RA_CONFIG
        @see MPU6050_CFG_DLPF_CFG_BIT
        @see MPU6050_CFG_DLPF_CFG_LENGTH
        '''

        return self.readBits(MPU6050_RA_CONFIG, MPU6050_CFG_DLPF_CFG_BIT, MPU6050_CFG_DLPF_CFG_LENGTH)

    def setDLPFMode(self, mode) :
        '''!
        Set digital low-pass filter configuration.
        @param mode New DLFP configuration setting
        @see getDLPFBandwidth()
        @see MPU6050_DLPF_BW_256
        @see MPU6050_RA_CONFIG
        @see MPU6050_CFG_DLPF_CFG_BIT
        @see MPU6050_CFG_DLPF_CFG_LENGTH
        '''
        writeBits(MPU6050_RA_CONFIG, MPU6050_CFG_DLPF_CFG_BIT, MPU6050_CFG_DLPF_CFG_LENGTH)


    # SELF TEST FACTORY TRIM VALUES

    def getAccelXSelfTestFactoryTrim(self) :
        '''!
        Get self-test factory trim value for accelerometer X axis.
        @return factory trim value
        @see MPU6050_RA_SELF_TEST_X
        '''
        tmp1 = self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_SELF_TEST_X,1)[0]
        tmp2 = self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_SELF_TEST_A,1)[0]
        return (tmp1 >>3) | ((tmp2 >>4) & 0x03)
                             
    def getAccelYSelfTestFactoryTrim(self) :
        '''!
        Get self-test factory trim value for accelerometer Y axis.
        @return factory trim value
        @see MPU6050_RA_SELF_TEST_Y
        '''
        tmp1 = self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_SELF_TEST_Y,1)[0]
        tmp2 = self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_SELF_TEST_A,1)[0]
        return (tmp1 >>3) | ((tmp2 >>4) & 0x03)


    def getAccelZSelfTestFactoryTrim(self) :
        '''!
        Get self-test factory trim value for accelerometer Z axis.
        @return factory trim value
        @see MPU6050_RA_SELF_TEST_Z
        '''
        tmp = self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_SELF_TEST_Z,2)
        return (tmp[0]>>3) | (tmp[1] & 0x03);        

    def getGyroXSelfTestFactoryTrim(self) :
        '''!
        Get self-test factory trim value for gyro X axis.
        @return factory trim value
        @see MPU6050_RA_SELF_TEST_X
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_SELF_TEST_X,1)[0] &0x1f

    def getGyroYSelfTestFactoryTrim(self) :
        '''!
        Get self-test factory trim value for gyro Y axis.
        @return factory trim value
        @see MPU6050_RA_SELF_TEST_Y
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_SELF_TEST_Y,1)[0] &0x1f

    def getGyroZSelfTestFactoryTrim(self) :
        '''!
        Get self-test factory trim value for gyro Z axis.
        @return factory trim value
        @see MPU6050_RA_SELF_TEST_Z
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_SELF_TEST_Z,1)[0] &0x1f
    
    # FF_THR register
    def getFreefallDetectionThreshold(self) :
        '''!
        Get free-fall event acceleration threshold.
        This register configures the detection threshold for Free Fall event
        detection. The unit of FF_THR is 1LSB = 2mg. Free Fall is detected when the
        absolute value of the accelerometer measurements for the three axes are each
        less than the detection threshold. This condition increments the Free Fall
        duration counter (Register 30). The Free Fall interrupt is triggered when the
        Free Fall duration counter reaches the time specified in FF_DUR.

        For more details on the Free Fall detection interrupt, see Section 8.2 of the
        MPU-6000/MPU-6050 Product Specification document as well as Registers 56 and
        58 of this document.

        @return Current free-fall acceleration threshold value (LSB = 2mg)
        @see MPU6050_RA_FF_THR
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_FF_THR,1)[0]

    def setFreefallDetectionThreshold(self,threshold) :
        '''
        Get free-fall event acceleration threshold.
        @param threshold New free-fall acceleration threshold value (LSB = 2mg)
        @see getFreefallDetectionThreshold()
        @see MPU6050_RA_FF_THR
        '''
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_FF_THR, threshold)

    # FF_DUR register

    def getFreefallDetectionDuration(self) :
        '''!
        Get free-fall event duration threshold.
        This register configures the duration counter threshold for Free Fall event
        detection. The duration counter ticks at 1kHz, therefore FF_DUR has a unit
        of 1 LSB = 1 ms.

        The Free Fall duration counter increments while the absolute value of the
        accelerometer measurements are each less than the detection threshold
        (Register 29). The Free Fall interrupt is triggered when the Free Fall
        duration counter reaches the time specified in this register.

        For more details on the Free Fall detection interrupt, see Section 8.2 of
        the MPU-6000/MPU-6050 Product Specification document as well as Registers 56
        and 58 of this document.

        @return Current free-fall duration threshold value (LSB = 1ms)
        @see MPU6050_RA_FF_DUR
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_FF_DUR,1)[0]

    def setFreefallDetectionDuration(self,duration) :
        '''
        Set free-fall event duration threshold.
        @param duration New free-fall duration threshold value (LSB = 1ms)
        @see getFreefallDetectionDuration()
        @see MPU6050_RA_FF_DUR
        '''
        tmp = bytearray(1)
        tmp[0] = duration
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_FF_DUR, tmp)

    # MOT_THR register
    def getMotionDetectionThreshold(self) :
        '''!
        Get motion detection event acceleration threshold.
        This register configures the detection threshold for Motion interrupt
        generation. The unit of MOT_THR is 1LSB = 2mg. Motion is detected when the
        absolute value of any of the accelerometer measurements exceeds this Motion
        detection threshold. This condition increments the Motion detection duration
        counter (Register 32). The Motion detection interrupt is triggered when the
        Motion Detection counter reaches the time count specified in MOT_DUR
        (Register 32).

        The Motion interrupt will indicate the axis and polarity of detected motion
        in MOT_DETECT_STATUS (Register 97).

        For more details on the Motion detection interrupt, see Section 8.3 of the
        MPU-6000/MPU-6050 Product Specification document as well as Registers 56 and
        58 of this document.

        @return Current motion detection acceleration threshold value (LSB = 2mg)
        @see MPU6050_RA_MOT_THR
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_MOT_THR,1)[0]

    def setMotionDetectionThreshold(self,threshold) :
        '''!
        Set motion detection event acceleration threshold.
        @param threshold New motion detection acceleration threshold value (LSB = 2mg)
        @see getMotionDetectionThreshold()
        @see MPU6050_RA_MOT_THR
        '''
        tmp = bytearray(1)
        tmp[0] = threshold
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_MOT_THR, tmp)

    #  MOT_DUR register

    def getMotionDetectionDuration(self) :
        '''!
        Get motion detection event duration threshold.
        This register configures the duration counter threshold for Motion interrupt
        generation. The duration counter ticks at 1 kHz, therefore MOT_DUR has a unit
        of 1LSB = 1ms. The Motion detection duration counter increments when the
        absolute value of any of the accelerometer measurements exceeds the Motion
        detection threshold (Register 31). The Motion detection interrupt is
        triggered when the Motion detection counter reaches the time count specified
        in this register.

        For more details on the Motion detection interrupt, see Section 8.3 of the
        MPU-6000/MPU-6050 Product Specification document.

        @return Current motion detection duration threshold value (LSB = 1ms)
        @see MPU6050_RA_MOT_DUR
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_MOT_DUR,1)[0]
        
    def setMotionDetectionDuration(self,duration) :
        '''!
        Set motion detection event duration threshold.
        @param duration New motion detection duration threshold value (LSB = 1ms)
        @see getMotionDetectionDuration()
        @see MPU6050_RA_MOT_DUR
        '''
        tmp = bytearray(1)
        tmp[0] = duration
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_MOT_DUR, tmp)

        
    # ZRMOT_THR register
    def getZeroMotionDetectionThreshold(self) :
        '''!
        Get zero motion detection event acceleration threshold.
        This register configures the detection threshold for Zero Motion interrupt
        generation. The unit of ZRMOT_THR is 1LSB = 2mg. Zero Motion is detected when
        the absolute value of the accelerometer measurements for the 3 axes are each
        less than the detection threshold. This condition increments the Zero Motion
        duration counter (Register 34). The Zero Motion interrupt is triggered when
        the Zero Motion duration counter reaches the time count specified in
        ZRMOT_DUR (Register 34).

        Unlike Free Fall or Motion detection, Zero Motion detection triggers an
        interrupt both when Zero Motion is first detected and when Zero Motion is no
        longer detected.

        When a zero motion event is detected, a Zero Motion Status will be indicated
        in the MOT_DETECT_STATUS register (Register 97). When a motion-to-zero-motion
        condition is detected, the status bit is set to 1. When a zero-motion-to-
        motion condition is detected, the status bit is set to 0.

        For more details on the Zero Motion detection interrupt, see Section 8.4 of
        the MPU-6000/MPU-6050 Product Specification document as well as Registers 56
        and 58 of this document.

        @return Current zero motion detection acceleration threshold value (LSB = 2mg)
        @see MPU6050_RA_ZRMOT_THR
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ZRMOT_THR,1)[0]

    def setZeroMotionDetectionThreshold(self,threshold) :
        '''!
        Set zero motion detection event acceleration threshold.
        @param threshold New zero motion detection acceleration threshold value (LSB = 2mg)
        @see getZeroMotionDetectionThreshold()
        @see MPU6050_RA_ZRMOT_THR
        '''
        tmp = bytearray(1)
        tmp[0] = threshold
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_ZRMOT_THR, tmp)
        
    # ZRMOT_DUR register
    def getZeroMotionDetectionDuration(self) :
        '''!
        Get zero motion detection event duration threshold.
        This register configures the duration counter threshold for Zero Motion
        interrupt generation. The duration counter ticks at 16 Hz, therefore
        ZRMOT_DUR has a unit of 1 LSB = 64 ms. The Zero Motion duration counter
        increments while the absolute value of the accelerometer measurements are
        each less than the detection threshold (Register 33). The Zero Motion
        interrupt is triggered when the Zero Motion duration counter reaches the time
        count specified in this register.

        For more details on the Zero Motion detection interrupt, see Section 8.4 of
        the MPU-6000/MPU-6050 Product Specification document, as well as Registers 56
        and 58 of this document.

        @return Current zero motion detection duration threshold value (LSB = 64ms)
        @see MPU6050_RA_ZRMOT_DUR
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ZRMOT_DUR,1)[0]

    def setZeroMotionDetectionDuration(self,duration) :
        '''!
        Set zero motion detection event duration threshold.
        @param duration New zero motion detection duration threshold value (LSB = 1ms)
        @see getZeroMotionDetectionDuration()
        @see MPU6050_RA_ZRMOT_DUR
        '''
        tmp = bytearray(1)
        tmp[0] = duration
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_ZRMOT_DUR, tmp)

    # FIFO_EN register
    
    def getTempFIFOEnabled(self) :
        '''!
        Get temperature FIFO enabled value.
        When set to 1, this bit enables TEMP_OUT_H and TEMP_OUT_L (Registers 65 and
        66) to be written into the FIFO buffer.
        @return Current temperature FIFO enabled value
        @see MPU6050_RA_FIFO_EN
        '''
        return self.readBit(MPU6050_RA_FIFO_EN, MPU6050_TEMP_FIFO_EN_BIT)

    def setTempFIFOEnabled(self,enabled) :
        '''!
        Set temperature FIFO enabled value.
        @param enabled New temperature FIFO enabled value
        @see getTempFIFOEnabled()
        @see MPU6050_RA_FIFO_EN
        '''
        self.writeBit(MPU6050_RA_FIFO_EN, MPU6050_TEMP_FIFO_EN_BIT, enabled)

        def getXGyroFIFOEnabled(self) :
            '''!
            Get gyroscope X-axis FIFO enabled value.
            When set to 1, this bit enables GYRO_XOUT_H and GYRO_XOUT_L (Registers 67 and
            68) to be written into the FIFO buffer.
            @return Current gyroscope X-axis FIFO enabled value
            @see MPU6050_RA_FIFO_EN
            '''
            return self.readBit(MPU6050_RA_FIFO_EN, MPU6050_XG_FIFO_EN_BIT)

    def setXGyroFIFOEnabled(self,enabled) :
        '''! 
        Set gyroscope X-axis FIFO enabled value.
        @param enabled New gyroscope X-axis FIFO enabled value
        @see getXGyroFIFOEnabled()
        @see MPU6050_RA_FIFO_EN
        '''
        self.writeBit(MPU6050_RA_FIFO_EN, MPU6050_XG_FIFO_EN_BIT, enabled)

    def getYGyroFIFOEnabled(self) :
        '''!
        Get gyroscope Y-axis FIFO enabled value.
        When set to 1, this bit enables GYRO_YOUT_H and GYRO_YOUT_L (Registers 69 and
        70) to be written into the FIFO buffer.
        @return Current gyroscope Y-axis FIFO enabled value
        @see MPU6050_RA_FIFO_EN
        '''
        return self.readBit(MPU6050_RA_FIFO_EN, MPU6050_YG_FIFO_EN_BIT)

    def setYGyroFIFOEnabled(self,enabled) :
        '''°!
        Set gyroscope Y-axis FIFO enabled value.
        @param enabled New gyroscope Y-axis FIFO enabled value
        @see getYGyroFIFOEnabled()
        @see MPU6050_RA_FIFO_EN
        '''
        self.writeBit(MPU6050_RA_FIFO_EN, MPU6050_YG_FIFO_EN_BIT, enabled)

    def getZGyroFIFOEnabled(self) :
        '''!
        Get gyroscope Z-axis FIFO enabled value.
        When set to 1, this bit enables GYRO_ZOUT_H and GYRO_ZOUT_L (Registers 71 and
        72) to be written into the FIFO buffer.
        @return Current gyroscope Z-axis FIFO enabled value
        @see MPU6050_RA_FIFO_EN
        '''
        return self.readBit(MPU6050_RA_FIFO_EN, MPU6050_ZG_FIFO_EN_BIT)

    def setZGyroFIFOEnabled(self,enabled) :
        '''!
        Set gyroscope Z-axis FIFO enabled value.
        @param enabled New gyroscope Z-axis FIFO enabled value
        @see getZGyroFIFOEnabled()
        @see MPU6050_RA_FIFO_EN
        '''
        self.writeBit(MPU6050_RA_FIFO_EN, MPU6050_ZG_FIFO_EN_BIT, enabled)

    def getAccelFIFOEnabled(self) :
        '''!
        Get accelerometer FIFO enabled value.
        When set to 1, this bit enables ACCEL_XOUT_H, ACCEL_XOUT_L, ACCEL_YOUT_H,
        ACCEL_YOUT_L, ACCEL_ZOUT_H, and ACCEL_ZOUT_L (Registers 59 to 64) to be
        written into the FIFO buffer.
        @return Current accelerometer FIFO enabled value
        @see MPU6050_RA_FIFO_EN
        '''
        return self.readBit(MPU6050_RA_FIFO_EN, MPU6050_ACCEL_FIFO_EN_BIT)

    def setAccelFIFOEnabled(self,enabled) :
        '''!
        Set accelerometer FIFO enabled value.
        @param enabled New accelerometer FIFO enabled value
        @see getAccelFIFOEnabled()
        @see MPU6050_RA_FIFO_EN
        '''
        self.writeBit(MPU6050_RA_FIFO_EN, MPU6050_ACCEL_FIFO_EN_BIT, enabled)

    def getSlave2FIFOEnabled(self) :
        '''!
        Get Slave 2 FIFO enabled value.
        When set to 1, this bit enables EXT_SENS_DATA registers (Registers 73 to 96)
        associated with Slave 2 to be written into the FIFO buffer.
        @return Current Slave 2 FIFO enabled value
        @see MPU6050_RA_FIFO_EN
        '''
        return self.readBit(MPU6050_RA_FIFO_EN, MPU6050_SLV2_FIFO_EN_BIT)

    def setSlave2FIFOEnabled(self,enabled) :
        '''!
        Set Slave 2 FIFO enabled value.
        @param enabled New Slave 2 FIFO enabled value
        @see getSlave2FIFOEnabled()
        @see MPU6050_RA_FIFO_EN
        '''
        self.writeBit(MPU6050_RA_FIFO_EN, MPU6050_SLV2_FIFO_EN_BIT)

    def getSlave1FIFOEnabled(self) :
        '''!
        Get Slave 1 FIFO enabled value.
        When set to 1, this bit enables EXT_SENS_DATA registers (Registers 73 to 96)
        associated with Slave 1 to be written into the FIFO buffer.
        @return Current Slave 1 FIFO enabled value
        @see MPU6050_RA_FIFO_EN
        '''
        return self.readBit(MPU6050_RA_FIFO_EN, MPU6050_SLV1_FIFO_EN_BIT)

    def setSlave1FIFOEnabled(self,enabled) :
        '''!
        Set Slave 1 FIFO enabled value.
        @param enabled New Slave 1 FIFO enabled value
        @see getSlave1FIFOEnabled()
        @see MPU6050_RA_FIFO_EN
        '''
        self.writeBit(MPU6050_RA_FIFO_EN, MPU6050_SLV1_FIFO_EN_BIT, enabled)

    def getSlave0FIFOEnabled(self) :
        '''!
        Get Slave 0 FIFO enabled value.
        When set to 1, this bit enables EXT_SENS_DATA registers (Registers 73 to 96)
        associated with Slave 0 to be written into the FIFO buffer.
        @return Current Slave 0 FIFO enabled value
        @see MPU6050_RA_FIFO_EN
        '''
        return self.readBit(MPU6050_RA_FIFO_EN, MPU6050_SLV0_FIFO_EN_BIT, buffer)

    def setSlave0FIFOEnabled(self,enabled) :
        '''!
        Set Slave 0 FIFO enabled value.
        @param enabled New Slave 0 FIFO enabled value
        @see getSlave0FIFOEnabled()
        @see MPU6050_RA_FIFO_EN
        '''
        self.writeBit(MPU6050_RA_FIFO_EN, MPU6050_SLV0_FIFO_EN_BIT, enabled)

    # I2C_MST_CTRL register

    def getMultiMasterEnabled(self) :
        '''!
        Get multi-master enabled value.
        Multi-master capability allows multiple I2C masters to operate on the same
        bus. In circuits where multi-master capability is required, set MULT_MST_EN
        to 1. This will increase current drawn by approximately 30uA.

        In circuits where multi-master capability is required, the state of the I2C
        bus must always be monitored by each separate I2C Master. Before an I2C
        Master can assume arbitration of the bus, it must first confirm that no other
        I2C Master has arbitration of the bus. When MULT_MST_EN is set to 1, the
        MPU-60X0's bus arbitration detection logic is turned on, enabling it to
        detect when the bus is available.

        @return Current multi-master enabled value
        @see MPU6050_RA_I2C_MST_CTRL
        '''
        return self.readBit(MPU6050_RA_I2C_MST_CTRL, MPU6050_MULT_MST_EN_BIT)

    def setMultiMasterEnabled(self,enabled) :
        '''!
        Set multi-master enabled value.
        @param enabled New multi-master enabled value
        @see getMultiMasterEnabled()
        @see MPU6050_RA_I2C_MST_CTRL
        '''
        self.writeBit(MPU6050_RA_I2C_MST_CTRL, MPU6050_MULT_MST_EN_BIT, enabled)

    def getWaitForExternalSensorEnabled(self) :
        '''!
        Get wait-for-external-sensor-data enabled value.
        When the WAIT_FOR_ES bit is set to 1, the Data Ready interrupt will be
        delayed until External Sensor data from the Slave Devices are loaded into the
        EXT_SENS_DATA registers. This is used to ensure that both the internal sensor
        data (i.e. from gyro and accel) and external sensor data have been loaded to
        their respective data registers (i.e. the data is synced) when the Data Ready
        interrupt is triggered.

        @return Current wait-for-external-sensor-data enabled value
        @see MPU6050_RA_I2C_MST_CTRL
        '''
        return self.readBit(MPU6050_RA_I2C_MST_CTRL, MPU6050_WAIT_FOR_ES_BIT)

    def setWaitForExternalSensorEnabled(self,enabled) :
        '''!
        Set wait-for-external-sensor-data enabled value.
        @param enabled New wait-for-external-sensor-data enabled value
        @see getWaitForExternalSensorEnabled()
        @see MPU6050_RA_I2C_MST_CTRL
        '''
        writeBit(MPU6050_RA_I2C_MST_CTRL, MPU6050_WAIT_FOR_ES_BIT, enabled)

    def getSlave3FIFOEnabled(self) :
        '''!
        Get Slave 3 FIFO enabled value.
        When set to 1, this bit enables EXT_SENS_DATA registers (Registers 73 to 96)
        associated with Slave 3 to be written into the FIFO buffer.
        @return Current Slave 3 FIFO enabled value
        @see MPU6050_RA_MST_CTRL
        '''
        return self.readBit(MPU6050_RA_I2C_MST_CTRL, MPU6050_SLV_3_FIFO_EN_BIT)

    def setSlave3FIFOEnabled(self,enabled) :
        '''!
        Set Slave 3 FIFO enabled value.
        @param enabled New Slave 3 FIFO enabled value
        @see getSlave3FIFOEnabled()
        @see MPU6050_RA_MST_CTRL
        '''
        self.writeBit(MPU6050_RA_I2C_MST_CTRL, MPU6050_SLV_3_FIFO_EN_BIT, enabled)

    def getSlaveReadWriteTransitionEnabled(self) :
        '''!
        Get slave read/write transition enabled value.
        The I2C_MST_P_NSR bit configures the I2C Master's transition from one slave
        read to the next slave read. If the bit equals 0, there will be a restart
        between reads. If the bit equals 1, there will be a stop followed by a start
        of the following read. When a write transaction follows a read transaction,
        the stop followed by a start of the successive write will be always used.
 
        @return Current slave read/write transition enabled value
        @see MPU6050_RA_I2C_MST_CTRL
        '''
        return self.readBit(MPU6050_RA_I2C_MST_CTRL, MPU6050_I2C_MST_P_NSR_BIT)

    def setSlaveReadWriteTransitionEnabled(self,enabled) :
        '''!
        Set slave read/write transition enabled value.
        @param enabled New slave read/write transition enabled value
        @see getSlaveReadWriteTransitionEnabled()
        @see MPU6050_RA_I2C_MST_CTRL
        '''
        self.writeBit(MPU6050_RA_I2C_MST_CTRL, MPU6050_I2C_MST_P_NSR_BIT, enabled)


    def getMasterClockSpeed(self) :
        '''!
        Get I2C master clock speed.
        I2C_MST_CLK is a 4 bit unsigned value which configures a divider on the
        MPU-60X0 internal 8MHz clock. It sets the I2C master clock speed according to
        the following table:

        <pre>
        I2C_MST_CLK | I2C Master Clock Speed | 8MHz Clock Divider
        ------------+------------------------+-------------------
        0           | 348kHz                 | 23
        1           | 333kHz                 | 24
        2           | 320kHz                 | 25
        3           | 308kHz                 | 26
        4           | 296kHz                 | 27
        5           | 286kHz                 | 28
        6           | 276kHz                 | 29
        7           | 267kHz                 | 30
        8           | 258kHz                 | 31
        9           | 500kHz                 | 16
        10          | 471kHz                 | 17
        11          | 444kHz                 | 18
        12          | 421kHz                 | 19
        13          | 400kHz                 | 20
        14          | 381kHz                 | 21
        15          | 364kHz                 | 22
        </pre>

        @return Current I2C master clock speed
        @see MPU6050_RA_I2C_MST_CTRL
        '''
        return self.readBits(MPU6050_RA_I2C_MST_CTRL, MPU6050_I2C_MST_CLK_BIT, MPU6050_I2C_MST_CLK_LENGTH)

    def setMasterClockSpeed(self,speed) :
        '''!
        Set I2C master clock speed.
        @reparam speed Current I2C master clock speed
        @see MPU6050_RA_I2C_MST_CTRL
        '''
        self.writeBits(MPU6050_RA_I2C_MST_CTRL, MPU6050_I2C_MST_CLK_BIT, MPU6050_I2C_MST_CLK_LENGTH, speed)


    #I2C_SLV* registers (Slave 0-3)
    
    def getSlaveAddress(num) :
        '''!
        Get the I2C address of the specified slave (0-3).
        Note that Bit 7 (MSB) controls read/write mode. If Bit 7 is set, it's a read
        operation, and if it is cleared, then it's a write operation. The remaining
        bits (6-0) are the 7-bit device address of the slave device.

        In read mode, the result of the read is placed in the lowest available 
        EXT_SENS_DATA register. For further information regarding the allocation of
        read results, please refer to the EXT_SENS_DATA register description
        (Registers 73 - 96).

        The MPU-6050 supports a total of five slaves, but Slave 4 has unique
        characteristics, and so it has its own functions (getSlave4* and setSlave4*).

        I2C data transactions are performed at the Sample Rate, as defined in
        Register 25. The user is responsible for ensuring that I2C data transactions
        to and from each enabled Slave can be completed within a single period of the
        Sample Rate.

        The I2C slave access rate can be reduced relative to the Sample Rate. This
        reduced access rate is determined by I2C_MST_DLY (Register 52). Whether a
        slave's access rate is reduced relative to the Sample Rate is determined by
        I2C_MST_DELAY_CTRL (Register 103).

        The processing order for the slaves is fixed. The sequence followed for
        processing the slaves is Slave 0, Slave 1, Slave 2, Slave 3 and Slave 4. If a
        particular Slave is disabled it will be skipped.

        Each slave can either be accessed at the sample rate or at a reduced sample
        rate. In a case where some slaves are accessed at the Sample Rate and some
        slaves are accessed at the reduced rate, the sequence of accessing the slaves
        (Slave 0 to Slave 4) is still followed. However, the reduced rate slaves will
        be skipped if their access rate dictates that they should not be accessed
        during that particular cycle. For further information regarding the reduced
        access rate, please refer to Register 52. Whether a slave is accessed at the
        Sample Rate or at the reduced rate is determined by the Delay Enable bits in
        Register 103.

        @param num Slave number (0-3)
        @return Current address for specified slave
        @see MPU6050_RA_I2C_SLV0_ADDR
        '''
        if num > 3:
            return 0
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_I2C_SLV0_ADDR + num*3,1)[0]

    def setSlaveAddress(self,num, address) :
        '''!
        Set the I2C address of the specified slave (0-3).
        @param num Slave number (0-3)
        @param address New address for specified slave
        @see getSlaveAddress()
        @see MPU6050_RA_I2C_SLV0_ADDR
        '''
        if (num > 3) :
            return
        tmp = bytearray[1]
        tmp[0] = address
        self.i2c.writeto_mem(self.mpu6050_,MPU6050_RA_I2C_SLV0_ADDR + num*3,tmp)

    def getSlaveRegister(self,num) :
        '''
        Get the active internal register for the specified slave (0-3).
        Read/write operations for this slave will be done to whatever internal
        register address is stored in this MPU register.

        The MPU-6050 supports a total of five slaves, but Slave 4 has unique
        characteristics, and so it has its own functions.

        @param num Slave number (0-3)
        @return Current active register for specified slave
        @see MPU6050_RA_I2C_SLV0_REG
        '''
        if (num > 3) :
            return 0
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_I2C_SLV0_REG + num*3,1)[0]

    def setSlaveRegister(self,num,reg) :
        '''!
        Set the active internal register for the specified slave (0-3).
        @param num Slave number (0-3)
        @param reg New active register for specified slave
        @see getSlaveRegister()
        @see MPU6050_RA_I2C_SLV0_REG
        '''
        if (num > 3) :
            return
        tmp = bytearray(1)
        tmp[0] = address
        self.i2c.writeto_mem(self.mpu6050_,MPU6050_RA_I2C_SLV0_REG + num*3,tmp)

    def getSlaveEnabled(self,num) :
        '''
        Get the enabled value for the specified slave (0-3).
        When set to 1, this bit enables Slave 0 for data transfer operations. When
        cleared to 0, this bit disables Slave 0 from data transfer operations.
        @param num Slave number (0-3)
        @return Current enabled value for specified slave
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''
        if (num > 3) :
            return 0
        return self.readBit(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_EN_BIT)

    def setSlaveEnabled(self,num,enabled) :
        '''!
        Set the enabled value for the specified slave (0-3).
        @param num Slave number (0-3)
        @param enabled New enabled value for specified slave
        @see getSlaveEnabled()
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''
        if (num > 3) :
            return 
        self.writeBit(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_EN_BIT, enabled)

    def getSlaveWordByteSwap(self,num) :
        '''!
        Get word pair byte-swapping enabled for the specified slave (0-3).
        When set to 1, this bit enables byte swapping. When byte swapping is enabled,
        the high and low bytes of a word pair are swapped. Please refer to
        I2C_SLV0_GRP for the pairing convention of the word pairs. When cleared to 0,
        bytes transferred to and from Slave 0 will be written to EXT_SENS_DATA
        registers in the order they were transferred.
 
        @param num Slave number (0-3)
        @return Current word pair byte-swapping enabled value for specified slave
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''

        if (num > 3) :
            return 0
        return self.readBit(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_BYTE_SW_BIT)

    def setSlaveWordByteSwap(self,num,enabled) :
        '''!
        Set word pair byte-swapping enabled for the specified slave (0-3).
        @param num Slave number (0-3)
        @param enabled New word pair byte-swapping enabled value for specified slave
        @see getSlaveWordByteSwap()
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''
        if (num > 3) :
            return
        self.writeBit(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_BYTE_SW_BIT, enabled)

    def getSlaveWriteMode(self,num) :
        '''!
        Get write mode for the specified slave (0-3).
        When set to 1, the transaction will read or write data only. When cleared to
        0, the transaction will write a register address prior to reading or writing
        data. This should equal 0 when specifying the register address within the
        Slave device to/from which the ensuing data transaction will take place.
 
        @param num Slave number (0-3)
        @return Current write mode for specified slave (0 = register address + data, 1 = data only)
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''
        if (num > 3) :
            return 0
        return self.readBit(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_REG_DIS_BIT)

    def setSlaveWriteMode(self,num,mode) :
        '''!
        Set write mode for the specified slave (0-3).
        @param num Slave number (0-3)
        @param mode New write mode for specified slave (0 = register address + data, 1 = data only)
        @see getSlaveWriteMode()
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''
        if (num > 3) :
            return
        self.writeBit(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_REG_DIS_BIT, mode)

    def getSlaveWordGroupOffset(self,num) :
        '''!
        Get word pair grouping order offset for the specified slave (0-3).
        This sets specifies the grouping order of word pairs received from registers.
        When cleared to 0, bytes from register addresses 0 and 1, 2 and 3, etc (even,
        then odd register addresses) are paired to form a word. When set to 1, bytes
        from register addresses are paired 1 and 2, 3 and 4, etc. (odd, then even
        register addresses) are paired to form a word.
 
        @param num Slave number (0-3)
        @return Current word pair grouping order offset for specified slave
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''
        if (num > 3) :
            return 0
        return self.readBit(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_GRP_BIT)

    def setSlaveWordGroupOffset(self,num,enabled) :
        '''!
        Set word pair grouping order offset for the specified slave (0-3).
        @param num Slave number (0-3)
        @param enabled New word pair grouping order offset for specified slave
        @see getSlaveWordGroupOffset()
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''
        if (num > 3) :
            return
        self.writeBit(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_GRP_BIT, enabled)

    def getSlaveDataLength(self,num) :
        '''!
        Get number of bytes to read for the specified slave (0-3).
        Specifies the number of bytes transferred to and from Slave 0. Clearing this
        bit to 0 is equivalent to disabling the register by writing 0 to I2C_SLV0_EN.
        @param num Slave number (0-3)
        @return Number of bytes to read for specified slave
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''
        if (num > 3) :
            return 0
        return self.readBits(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_LEN_BIT, MPU6050_I2C_SLV_LEN_LENGTH)
        
    def setSlaveDataLength(self,num,length) :
        '''!
        Set number of bytes to read for the specified slave (0-3).
        @param num Slave number (0-3)
        @param length Number of bytes to read for specified slave
        @see getSlaveDataLength()
        @see MPU6050_RA_I2C_SLV0_CTRL
        '''
        if (num > 3) :
            return
        self.writeBits(MPU6050_RA_I2C_SLV0_CTRL + num*3, MPU6050_I2C_SLV_LEN_BIT, MPU6050_I2C_SLV_LEN_LENGTH)


    # I2C_SLV* registers (Slave 4)

    def getSlave4Address(self) :
        '''!
        Get the I2C address of Slave 4.
        Note that Bit 7 (MSB) controls read/write mode. If Bit 7 is set, it's a read
        operation, and if it is cleared, then it's a write operation. The remaining
        bits (6-0) are the 7-bit device address of the slave device.
 
        @return Current address for Slave 4
        @see getSlaveAddress()
        @see MPU6050_RA_I2C_SLV4_ADDR
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_I2C_SLV4_ADDR, 1)[0]

    def setSlave4Address(self,address) :
        '''!
        Set the I2C address of Slave 4.
        @param address New address for Slave 4
        @see getSlave4Address()
        @see MPU6050_RA_I2C_SLV4_ADDR
        '''
        tmp = bytearray(1)
        tmp[0] = address
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_I2C_SLV4_ADDR, tmp)

    def getSlave4Register(self) :
        '''!
        Get the active internal register for the Slave 4.
        Read/write operations for this slave will be done to whatever internal
        register address is stored in this MPU register.
        
        @return Current active register for Slave 4
        @see MPU6050_RA_I2C_SLV4_REG
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_I2C_SLV4_REG, 1)[0]

    def setSlave4Register(self,reg) :
        '''!
        Set the active internal register for Slave 4.
        @param reg New active register for Slave 4
        @see getSlave4Register()
        @see MPU6050_RA_I2C_SLV4_REG
        '''
        tmp = bytearray(1)
        tmp[0] = reg
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_I2C_SLV4_REG, tmp)

    def setSlave4OutputByte(self,data) :
        '''!
        Set new byte to write to Slave 4.
        This register stores the data to be written into the Slave 4. If I2C_SLV4_RW
        is set 1 (set to read), this register has no effect.
        @param data New byte to write to Slave 4
        @see MPU6050_RA_I2C_SLV4_DO
        '''
        tmp = bytearray(1)
        tmp[0] = data
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_I2C_SLV4_DO, tmp)

    def getSlave4Enabled(self) :
        '''!
        Get the enabled value for the Slave 4.
        When set to 1, this bit enables Slave 4 for data transfer operations. When
        cleared to 0, this bit disables Slave 4 from data transfer operations.
        @return Current enabled value for Slave 4
        @see MPU6050_RA_I2C_SLV4_CTRL
        '''
        return readBit(MPU6050_RA_I2C_SLV4_CTRL, MPU6050_I2C_SLV4_EN_BIT)

    def setSlave4Enabled(self,enabled) :
        '''!
        Set the enabled value for Slave 4.
        @param enabled New enabled value for Slave 4
        @see getSlave4Enabled()
        @see MPU6050_RA_I2C_SLV4_CTRL
        '''
        self.writeBit(MPU6050_RA_I2C_SLV4_CTRL, MPU6050_I2C_SLV4_EN_BIT, enabled)

    def getSlave4InterruptEnabled(self) :
        '''!
        Get the enabled value for Slave 4 transaction interrupts.
        When set to 1, this bit enables the generation of an interrupt signal upon
        completion of a Slave 4 transaction. When cleared to 0, this bit disables the
        generation of an interrupt signal upon completion of a Slave 4 transaction.
        The interrupt status can be observed in Register 54.
 
        @return Current enabled value for Slave 4 transaction interrupts.
        @see MPU6050_RA_I2C_SLV4_CTRL
        '''

        return self.readBit(MPU6050_RA_I2C_SLV4_CTRL, MPU6050_I2C_SLV4_INT_EN_BIT)

    def setSlave4InterruptEnabled(self,enabled) :
        '''!
        Set the enabled value for Slave 4 transaction interrupts.
        @param enabled New enabled value for Slave 4 transaction interrupts.
        @see getSlave4InterruptEnabled()
        @see MPU6050_RA_I2C_SLV4_CTRL
        '''
        self.writeBit(MPU6050_RA_I2C_SLV4_CTRL, MPU6050_I2C_SLV4_INT_EN_BIT, enabled)

    def getSlave4WriteMode(self) :
        '''!
        Get write mode for Slave 4.
        When set to 1, the transaction will read or write data only. When cleared to
        0, the transaction will write a register address prior to reading or writing
        data. This should equal 0 when specifying the register address within the
        Slave device to/from which the ensuing data transaction will take place.
 
        @return Current write mode for Slave 4 (0 = register address + data, 1 = data only)
        @see MPU6050_RA_I2C_SLV4_CTRL
        '''
        return self.readBit(MPU6050_RA_I2C_SLV4_CTRL, MPU6050_I2C_SLV4_REG_DIS_BIT);

    def setSlave4WriteMode(self,mode) :
        '''!
        Set write mode for the Slave 4.
        @param mode New write mode for Slave 4 (0 = register address + data, 1 = data only)
        @see getSlave4WriteMode()
        @see MPU6050_RA_I2C_SLV4_CTRL
        '''
        self.writeBit(MPU6050_RA_I2C_SLV4_CTRL, MPU6050_I2C_SLV4_REG_DIS_BIT, mode)

    def getSlave4MasterDelay(self) :
        '''!
        Get Slave 4 master delay value.
        This configures the reduced access rate of I2C slaves relative to the Sample
        Rate. When a slave's access rate is decreased relative to the Sample Rate,
        the slave is accessed every:
 
        1 / (1 + I2C_MST_DLY) samples
        
        This base Sample Rate in turn is determined by SMPLRT_DIV (register 25) and
        DLPF_CFG (register 26). Whether a slave's access rate is reduced relative to
        the Sample Rate is determined by I2C_MST_DELAY_CTRL (register 103). For
        further information regarding the Sample Rate, please refer to register 25.
 
        @return Current Slave 4 master delay value
        @see MPU6050_RA_I2C_SLV4_CTRL
        '''
        return self.readBits(MPU6050_RA_I2C_SLV4_CTRL, MPU6050_I2C_SLV4_MST_DLY_BIT, MPU6050_I2C_SLV4_MST_DLY_LENGTH)

    def setSlave4MasterDelay(self,delay) :
        '''!
        Set Slave 4 master delay value.
        @param delay New Slave 4 master delay value
        @see getSlave4MasterDelay()
        @see MPU6050_RA_I2C_SLV4_CTRL
        '''
        self.writeBits(MPU6050_RA_I2C_SLV4_CTRL, MPU6050_I2C_SLV4_MST_DLY_BIT, MPU6050_I2C_SLV4_MST_DLY_LENGTH, delay)

    def getSlave4InputByte(self) :
        '''!
        Get last available byte read from Slave 4.
        This register stores the data read from Slave 4. This field is populated
        after a read transaction.
        @return Last available byte read from to Slave 4
        @see MPU6050_RA_I2C_SLV4_DI
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_I2C_SLV4_DI, 1)[0]

    # I2C_MST_STATUS register

    def getPassthroughStatus(self) :
        '''!
        Get FSYNC interrupt status.
        This bit reflects the status of the FSYNC interrupt from an external device
        into the MPU-60X0. This is used as a way to pass an external interrupt
        through the MPU-60X0 to the host application processor. When set to 1, this
        bit will cause an interrupt if FSYNC_INT_EN is asserted in INT_PIN_CFG
        (Register 55).
        @return FSYNC interrupt status
        @see MPU6050_RA_I2C_MST_STATUS
        '''
        return self.readBit(MPU6050_RA_I2C_MST_STATUS, MPU6050_MST_PASS_THROUGH_BIT)

    def getSlave4IsDone(self) :
        '''!
        Get Slave 4 transaction done status.
        Automatically sets to 1 when a Slave 4 transaction has completed. This
        triggers an interrupt if the I2C_MST_INT_EN bit in the INT_ENABLE register
        (Register 56) is asserted and if the SLV_4_DONE_INT bit is asserted in the
        I2C_SLV4_CTRL register (Register 52).
        @return Slave 4 transaction done status
        @see MPU6050_RA_I2C_MST_STATUS
        '''
        return self.readBit(MPU6050_RA_I2C_MST_STATUS, MPU6050_MST_I2C_SLV4_DONE_BIT)

    def getLostArbitration(self) :
        '''!
        Get master arbitration lost status.
        This bit automatically sets to 1 when the I2C Master has lost arbitration of
        the auxiliary I2C bus (an error condition). This triggers an interrupt if the
        I2C_MST_INT_EN bit in the INT_ENABLE register (Register 56) is asserted.
        @return Master arbitration lost status
        @see MPU6050_RA_I2C_MST_STATUS
        '''
        return self.readBit(MPU6050_RA_I2C_MST_STATUS, MPU6050_MST_I2C_LOST_ARB_BIT)

    def getSlave4Nack(self) :
        '''!
        Get Slave 4 NACK status.
        This bit automatically sets to 1 when the I2C Master receives a NACK in a
        transaction with Slave 4. This triggers an interrupt if the I2C_MST_INT_EN
        bit in the INT_ENABLE register (Register 56) is asserted.
        @return Slave 4 NACK interrupt status
        @see MPU6050_RA_I2C_MST_STATUS
        '''
        return self.readBit(MPU6050_RA_I2C_MST_STATUS, MPU6050_MST_I2C_SLV4_NACK_BIT)

    def getSlave3Nack(self) :
        '''!
        Get Slave 3 NACK status.
        This bit automatically sets to 1 when the I2C Master receives a NACK in a
        transaction with Slave 3. This triggers an interrupt if the I2C_MST_INT_EN
        bit in the INT_ENABLE register (Register 56) is asserted.
        @return Slave 3 NACK interrupt status
        @see MPU6050_RA_I2C_MST_STATUS
        '''
        return self.readBit(MPU6050_RA_I2C_MST_STATUS, MPU6050_MST_I2C_SLV3_NACK_BIT)

    def getSlave2Nack(self) :
        '''!
        Get Slave 2 NACK status.
        This bit automatically sets to 1 when the I2C Master receives a NACK in a
        transaction with Slave 2. This triggers an interrupt if the I2C_MST_INT_EN
        bit in the INT_ENABLE register (Register 56) is asserted.
        @return Slave 2 NACK interrupt status
        @see MPU6050_RA_I2C_MST_STATUS
        '''
        return self.readBit(MPU6050_RA_I2C_MST_STATUS, MPU6050_MST_I2C_SLV2_NACK_BIT)

    def getSlave1Nack(self) :
        '''!
        Get Slave 1 NACK status.
        This bit automatically sets to 1 when the I2C Master receives a NACK in a
        transaction with Slave 1. This triggers an interrupt if the I2C_MST_INT_EN
        bit in the INT_ENABLE register (Register 56) is asserted.
        @return Slave 1 NACK interrupt status
        @see MPU6050_RA_I2C_MST_STATUS
        '''
        return self.readBit(MPU6050_RA_I2C_MST_STATUS, MPU6050_MST_I2C_SLV1_NACK_BIT)

    def getSlave0Nack(self) :
        '''!
        Get Slave 0 NACK status.
        This bit automatically sets to 1 when the I2C Master receives a NACK in a
        transaction with Slave 0. This triggers an interrupt if the I2C_MST_INT_EN
        bit in the INT_ENABLE register (Register 56) is asserted.
        @return Slave 0 NACK interrupt status
        @see MPU6050_RA_I2C_MST_STATUS
        '''
        return self.readBit(MPU6050_RA_I2C_MST_STATUS, MPU6050_MST_I2C_SLV0_NACK_BIT)


    # INT_PIN_CFG register

    def getInterruptConfig(self) :
        '''!
        Get the interrupt configuration
        @return Current state of the interrupt config register
        @see MPU6050_RA_INT_PIN_CFG
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_INT_PIN_CFG, 1)[0]
    
    def getInterruptMode(self) :
        '''!
        Get interrupt logic level mode.
        Will be set 0 for active-high, 1 for active-low.
        @return Current interrupt mode (0=active-high, 1=active-low)
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_INT_LEVEL_BIT
        '''
        return self.readBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_INT_LEVEL_BIT)

    def setInterruptMode(self,mode) :
        '''!
        Set interrupt logic level mode.
        @param mode New interrupt mode (0=active-high, 1=active-low)
        @see getInterruptMode()
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_INT_LEVEL_BIT
        '''
        self.writeBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_INT_LEVEL_BIT, mode)

    def getInterruptDrive(self) :
        '''!
        Get interrupt drive mode.
        Will be set 0 for push-pull, 1 for open-drain.
        @return Current interrupt drive mode (0=push-pull, 1=open-drain)
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_INT_OPEN_BIT
        '''
        return self.readBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_INT_OPEN_BIT)

    def setInterruptDrive(self,drive) :
        '''!
        Set interrupt drive mode.
        @param drive New interrupt drive mode (0=push-pull, 1=open-drain)
        @see getInterruptDrive()
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_INT_OPEN_BIT
        '''
        self.writeBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_INT_OPEN_BIT)

    def getInterruptLatch(self) :
        '''!
        Get interrupt latch mode.
        Will be set 0 for 50us-pulse, 1 for latch-until-int-cleared.
        @return Current latch mode (0=50us-pulse, 1=latch-until-int-cleared)
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_LATCH_INT_EN_BIT
        '''
        return self.readBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_LATCH_INT_EN_BIT)

    def setInterruptLatch(self,latch) :
        '''!
        Set interrupt latch mode.
        @param latch New latch mode (0=50us-pulse, 1=latch-until-int-cleared)
        @see getInterruptLatch()
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_LATCH_INT_EN_BIT
        '''
        self.writeBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_LATCH_INT_EN_BIT, latch)

    def getInterruptLatchClear(self) :
        '''!
        Get interrupt latch clear mode.
        Will be set 0 for status-read-only, 1 for any-register-read.
        @return Current latch clear mode (0=status-read-only, 1=any-register-read)
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_INT_RD_CLEAR_BIT
        '''
        return self.readBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_INT_RD_CLEAR_BIT)

    def setInterruptLatchClear(self,clear) :
        '''!
        Set interrupt latch clear mode.
        @param clear New latch clear mode (0=status-read-only, 1=any-register-read)
        @see getInterruptLatchClear()
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_INT_RD_CLEAR_BIT
        '''
        self.writeBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_INT_RD_CLEAR_BIT, clear)

    def getFSyncInterruptLevel(self) :
        '''!
        Get FSYNC interrupt logic level mode.
        @return Current FSYNC interrupt mode (0=active-high, 1=active-low)
        @see getFSyncInterruptMode()
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_FSYNC_INT_LEVEL_BIT
        '''
        return self.readBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_FSYNC_INT_LEVEL_BIT)

    def setFSyncInterruptLevel(self,level) :
        '''!
        Set FSYNC interrupt logic level mode.
        @param mode New FSYNC interrupt mode (0=active-high, 1=active-low)
        @see getFSyncInterruptMode()
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_FSYNC_INT_LEVEL_BIT
        '''
        self.writeBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_FSYNC_INT_LEVEL_BIT, level)

    def getFSyncInterruptEnabled(self) :
        '''!
        Get FSYNC pin interrupt enabled setting.
        Will be set 0 for disabled, 1 for enabled.
        @return Current interrupt enabled setting
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_FSYNC_INT_EN_BIT
        '''
        return self.readBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_FSYNC_INT_EN_BIT)

    def setFSyncInterruptEnabled(self,enabled) :
        '''!
        Set FSYNC pin interrupt enabled setting.
        @param enabled New FSYNC pin interrupt enabled setting
        @see getFSyncInterruptEnabled()
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_FSYNC_INT_EN_BIT
        '''
        self.writeBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_FSYNC_INT_EN_BIT, enabled)

    def getI2CBypassEnabled(self) :
        '''!
        Get I2C bypass enabled status.
        When this bit is equal to 1 and I2C_MST_EN (Register 106 bit[5]) is equal to
        0, the host application processor will be able to directly access the
        auxiliary I2C bus of the MPU-60X0. When this bit is equal to 0, the host
        application processor will not be able to directly access the auxiliary I2C
        bus of the MPU-60X0 regardless of the state of I2C_MST_EN (Register 106
        bit[5]).
        @return Current I2C bypass enabled status
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_I2C_BYPASS_EN_BIT
        '''
        return self.readBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_I2C_BYPASS_EN_BIT)

    def setI2CBypassEnabled(selff,enabled) :
        '''!
        Set I2C bypass enabled status.
        When this bit is equal to 1 and I2C_MST_EN (Register 106 bit[5]) is equal to
        0, the host application processor will be able to directly access the
        auxiliary I2C bus of the MPU-60X0. When this bit is equal to 0, the host
        application processor will not be able to directly access the auxiliary I2C
        bus of the MPU-60X0 regardless of the state of I2C_MST_EN (Register 106
        bit[5]).
        @param enabled New I2C bypass enabled status
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_I2C_BYPASS_EN_BIT
        '''
        self.writeBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_I2C_BYPASS_EN_BIT)

    def getClockOutputEnabled(self) :
        '''!
        Get reference clock output enabled status.
        When this bit is equal to 1, a reference clock output is provided at the
        CLKOUT pin. When this bit is equal to 0, the clock output is disabled. For
        further information regarding CLKOUT, please refer to the MPU-60X0 Product
        Specification document.
        @return Current reference clock output enabled status
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_CLKOUT_EN_BIT
        '''
        return self.readBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_CLKOUT_EN_BIT)

    def setClockOutputEnabled(self,enabled) :
        '''!
        Set reference clock output enabled status.
        When this bit is equal to 1, a reference clock output is provided at the
        CLKOUT pin. When this bit is equal to 0, the clock output is disabled. For
        further information regarding CLKOUT, please refer to the MPU-60X0 Product
        Specification document.
        @param enabled New reference clock output enabled status
        @see MPU6050_RA_INT_PIN_CFG
        @see MPU6050_INTCFG_CLKOUT_EN_BIT
        '''
        self.writeBit(MPU6050_RA_INT_PIN_CFG, MPU6050_INTCFG_CLKOUT_EN_BIT, enabled)

    # INT_ENABLE register
    
    def getIntEnabled(self) :
        '''!
        Get full interrupt enabled status.
        Full register byte for all interrupts, for quick reading. Each bit will be
        set 0 for disabled, 1 for enabled.
        @return Current interrupt enabled status
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_FF_BIT
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_INT_ENABLE, 1)[0]

    def setIntEnabled(self,enabled) :
        '''!
        Set full interrupt enabled status.
        Full register byte for all interrupts, for quick reading. Each bit should be
        set 0 for disabled, 1 for enabled.
        @param enabled New interrupt enabled status
        @see getIntFreefallEnabled()
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_FF_BIT
        '''
        tmp = bytearray(1)
        tmp[0] = enabled
        self.i2c.writeto_mem(self.mpu6050_,MPU6050_RA_INT_ENABLE,tmp)

    def getIntFreefallEnabled(self) :
        '''!
        Get Free Fall interrupt enabled status.
        Will be set 0 for disabled, 1 for enabled.
        @return Current interrupt enabled status
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_FF_BIT
        '''
        return self.readBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_FF_BIT)

    def setIntFreefallEnabled(self,enabled) :
        '''!
        Set Free Fall interrupt enabled status.
        @param enabled New interrupt enabled status
        @see getIntFreefallEnabled()
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_FF_BIT
        '''
        writeBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_FF_BIT, enabled)

    def getIntMotionEnabled(self) :
        '''!
        Get Motion Detection interrupt enabled status.
        Will be set 0 for disabled, 1 for enabled.
        @return Current interrupt enabled status
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_MOT_BIT
        '''
        return self.readBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_MOT_BIT)

    def setIntMotionEnabled(self,enabled) :
        '''!
        Set Motion Detection interrupt enabled status.
        @param enabled New interrupt enabled status
        @see getIntMotionEnabled()
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_MOT_BIT
        '''
        self.writeBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_MOT_BIT, enabled)

    def getIntZeroMotionEnabled(self) :
        '''!
        Get Zero Motion Detection interrupt enabled status.
        Will be set 0 for disabled, 1 for enabled.
        @return Current interrupt enabled status
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_ZMOT_BIT
        '''
        return self.readBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_ZMOT_BIT)

    def setIntZeroMotionEnabled(self,enabled) :
        '''!
        Set Zero Motion Detection interrupt enabled status.
        @param enabled New interrupt enabled status
        @see getIntZeroMotionEnabled()
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_ZMOT_BIT
        '''
        self.writeBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_ZMOT_BIT, enabled)

    def getIntFIFOBufferOverflowEnabled(self) :        
        '''!
        Get FIFO Buffer Overflow interrupt enabled status.
        Will be set 0 for disabled, 1 for enabled.
        @return Current interrupt enabled status
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_FIFO_OFLOW_BIT
        '''
        return self.readBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_FIFO_OFLOW_BIT)

    def setIntFIFOBufferOverflowEnabled(self,enabled) :
        '''!
        Set FIFO Buffer Overflow interrupt enabled status.
        @param enabled New interrupt enabled status
        @see getIntFIFOBufferOverflowEnabled()
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_FIFO_OFLOW_BIT
        '''
        self.writeBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_FIFO_OFLOW_BIT, enabled)

    def getIntI2CMasterEnabled(self) :
        '''!
        Get I2C Master interrupt enabled status.
        This enables any of the I2C Master interrupt sources to generate an
        interrupt. Will be set 0 for disabled, 1 for enabled.
        @return Current interrupt enabled status
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_I2C_MST_INT_BIT
        '''
        return self.readBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_I2C_MST_INT_BIT)

    def setIntI2CMasterEnabled(self,enabled) :
        '''!
        Set I2C Master interrupt enabled status.
        @param enabled New interrupt enabled status
        @see getIntI2CMasterEnabled()
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_I2C_MST_INT_BIT
        '''
        self.writeBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_I2C_MST_INT_BIT, enabled)

    def getIntDataReadyEnabled(self) :
        '''!
        Get Data Ready interrupt enabled setting.
        This event occurs each time a write operation to all of the sensor registers
        has been completed. Will be set 0 for disabled, 1 for enabled.
        @return Current interrupt enabled status
        @see MPU6050_RA_INT_ENABLE
        @see MPU6050_INTERRUPT_DATA_RDY_BIT
        '''
        return self.readBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_DATA_RDY_BIT)

    def setIntDataReadyEnabled(self,enabled) :    
        '''!
        Set Data Ready interrupt enabled status.
        @param enabled New interrupt enabled status
        @see getIntDataReadyEnabled()
        @see MPU6050_RA_INT_CFG
        @see MPU6050_INTERRUPT_DATA_RDY_BIT
        '''
        self.writeBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_DATA_RDY_BIT, enabled)

    # INT_STATUS register

    def getIntStatus(self) :
        '''!
        Get full set of interrupt status bits.
        These bits clear to 0 after the register has been read. Very useful
        for getting multiple INT statuses, since each single bit read clears
        all of them because it has to read the whole byte.
        @return Current interrupt status
        @see MPU6050_RA_INT_STATUS
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_INT_STATUS, 1)[0]

    def getIntFreefallStatus(self) :
        '''!
        Get Free Fall interrupt status.
        This bit automatically sets to 1 when a Free Fall interrupt has been
        generated. The bit clears to 0 after the register has been read.
        @return Current interrupt status
        @see MPU6050_RA_INT_STATUS
        @see MPU6050_INTERRUPT_FF_BIT
        '''
        return self.readBit(MPU6050_RA_INT_STATUS, MPU6050_INTERRUPT_FF_BIT)

    def getIntMotionStatus(self) :
        '''!
        Get Motion Detection interrupt status.
        This bit automatically sets to 1 when a Motion Detection interrupt has been
        generated. The bit clears to 0 after the register has been read.
        @return Current interrupt status
        @see MPU6050_RA_INT_STATUS
        @see MPU6050_INTERRUPT_MOT_BIT
        '''
        return self.readBit(MPU6050_RA_INT_STATUS, MPU6050_INTERRUPT_MOT_BIT)

    def getIntZeroMotionStatus(self) :
        '''!
        Get Zero Motion Detection interrupt status.
        This bit automatically sets to 1 when a Zero Motion Detection interrupt has
        been generated. The bit clears to 0 after the register has been read.
        @return Current interrupt status
        @see MPU6050_RA_INT_STATUS
        @see MPU6050_INTERRUPT_ZMOT_BIT
        '''
        return self.readBit(MPU6050_RA_INT_STATUS, MPU6050_INTERRUPT_ZMOT_BIT)

    def getIntFIFOBufferOverflowStatus(self) :
        '''!
        Get FIFO Buffer Overflow interrupt status.
        This bit automatically sets to 1 when a Free Fall interrupt has been
        generated. The bit clears to 0 after the register has been read.
        @return Current interrupt status
        @see MPU6050_RA_INT_STATUS
        @see MPU6050_INTERRUPT_FIFO_OFLOW_BIT
        '''
        return self.readBit(MPU6050_RA_INT_STATUS, MPU6050_INTERRUPT_FIFO_OFLOW_BIT)

    def getIntI2CMasterStatus(self) :
        '''!
        Get I2C Master interrupt status.
        This bit automatically sets to 1 when an I2C Master interrupt has been
        generated. For a list of I2C Master interrupts, please refer to Register 54.
        The bit clears to 0 after the register has been read.
        @return Current interrupt status
        @see MPU6050_RA_INT_STATUS
        @see MPU6050_INTERRUPT_I2C_MST_INT_BIT
        '''
        returnself.readBit(MPU6050_RA_INT_STATUS, MPU6050_INTERRUPT_I2C_MST_INT_BIT)

    def getIntDataReadyStatus(self) :
        '''!
        Get Data Ready interrupt status.
        This bit automatically sets to 1 when a Data Ready interrupt has been
        generated. The bit clears to 0 after the register has been read.
        @return Current interrupt status
        @see MPU6050_RA_INT_STATUS
        @see MPU6050_INTERRUPT_DATA_RDY_BIT
        '''
        return self.readBit(MPU6050_RA_INT_STATUS, MPU6050_INTERRUPT_DATA_RDY_BIT)

    def bytesToInt(self,bytes):
        '''!
        The mpu6050 returns 16 bit signed values in 2 bytes. The bytes are joined and the resulting value
        converted to a Python integer
        @ param hi: the most significant 8 bits or the value
        @ param lo: the low significant bits
        @ return the signed integer value
        '''
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

    def intToBytes(self,value) :
        tmp = pack('>h', value)
        if self.debug:
            print("16 bit value: 0x{:02x}{:02x}".format(tmp[0],tmp[1]))
        return tmp
    
    def bytesToDoubleInt(self,bytes):
        '''!
        The mpu6050 returns 32 bit signed values in 4 bytes. The bytes are joined and the resulting value
        converted to a Python integer
        @ param bytes: the 4 bytes, highest significant byte first
        @ return the signed integer value
        '''
        val = bytes[0] << 24 | bytes[1] << 16 | bytes[2] <<8 | bytes[0] 
        if self.debug:
            print("value: 0x{:08x}".format(val))
        if not val & 0x80000000:           # positive 32 bit value
            if self.debug:
                print ("positive value: {:d}".format(val))
            return val
        else:
            val = -((val ^ 0xffffffff) + 1)
            if self.debug:
                print("negative value: {:d} ".format(val)) 
            return val
        
    # ACCEL_*OUT_* registers
    def getMotion9(self) :
        '''!
        Get raw 9-axis motion sensor readings (accel/gyro/compass).
        FUNCTION NOT FULLY IMPLEMENTED YET.
        @param ax 16-bit signed integer container for accelerometer X-axis value
        @param ay 16-bit signed integer container for accelerometer Y-axis value
        @param az 16-bit signed integer container for accelerometer Z-axis value
        @param gx 16-bit signed integer container for gyroscope X-axis value
        @param gy 16-bit signed integer container for gyroscope Y-axis value
        @param gz 16-bit signed integer container for gyroscope Z-axis value
        @param mx 16-bit signed integer container for magnetometer X-axis value
        @param my 16-bit signed integer container for magnetometer Y-axis value
        @param mz 16-bit signed integer container for magnetometer Z-axis value
        @see getMotion6()
        @see getAcceleration()
        @see getRotation()
        @see MPU6050_RA_ACCEL_XOUT_H
        '''
        mx = None # unused parameter
        my = None # unused parameter
        mz = None # unused parameter
    
        motion6 = getMotion6(ax, ay, az, gx, gy, gz)
        tmp = list(motion6)
        tmp += [mx,my,mz]
        # TODO: magnetometer integration
        return tuple(tmp)

    def getMotion6(self) :
        '''!
        Get raw 6-axis motion sensor readings (accel/gyro).
        Retrieves all currently available motion sensor values.
        @param ax 16-bit signed integer container for accelerometer X-axis value
        @param ay 16-bit signed integer container for accelerometer Y-axis value
        @param az 16-bit signed integer container for accelerometer Z-axis value
        @param gx 16-bit signed integer container for gyroscope X-axis value
        @param gy 16-bit signed integer container for gyroscope Y-axis value
        @param gz 16-bit signed integer container for gyroscope Z-axis value
        @see getAcceleration()
        @see getRotation()
        @see MPU6050_RA_ACCEL_XOUT_H
        '''
        ax = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_XOUT_H,2))
        ay = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_YOUT_H,2))
        az = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_ZOUT_H,2))

        gx = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_GYRO_XOUT_H,2))
        gy = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_GYRO_YOUT_H,2))
        gz = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_GYRO_ZOUT_H,2))

        return(ax,ay,az,gx,gy,gz)
    
    def getAcceleration(self) :
        '''!
        Get 3-axis accelerometer readings.
        These registers store the most recent accelerometer measurements.
        Accelerometer measurements are written to these registers at the Sample Rate
        as defined in Register 25.

        The accelerometer measurement registers, along with the temperature
        measurement registers, gyroscope measurement registers, and external sensor
        data registers, are composed of two sets of registers: an internal register
        set and a user-facing read register set.

        The data within the accelerometer sensors' internal register set is always
        updated at the Sample Rate. Meanwhile, the user-facing read register set
        duplicates the internal register set's data values whenever the serial
        interface is idle. This guarantees that a burst read of sensor registers will
        read measurements from the same sampling instant. Note that if burst reads
        are not used, the user is responsible for ensuring a set of single byte reads
        correspond to a single sampling instant by checking the Data Ready interrupt.

        Each 16-bit accelerometer measurement has a full scale defined in ACCEL_FS
        (Register 28). For each full scale setting, the accelerometers' sensitivity
        per LSB in ACCEL_xOUT is shown in the table below:

        <pre>
        AFS_SEL | Full Scale Range | LSB Sensitivity
        --------+------------------+----------------
        0       | +/- 2g           | 16384 LSB/mg
        1       | +/- 4g           | 8192 LSB/mg
        2       | +/- 8g           | 4096 LSB/mg
        3       | +/- 16g          | 2048 LSB/mg
        </pre>

        @param x 16-bit signed integer container for X-axis acceleration
        @param y 16-bit signed integer container for Y-axis acceleration
        @param z 16-bit signed integer container for Z-axis acceleration
        @return tuple (ax,ay,az)
        @see MPU6050_RA_GYRO_XOUT_H
        '''
        ax = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_XOUT_H,2))
        ay = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_YOUT_H,2))
        az = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_ZOUT_H,2))

        return (ax,ay,az)

    def getAccelerationX(self) :
        '''!
        Get X-axis accelerometer reading.
        @return X-axis acceleration measurement in 16-bit 2's complement format
        @see getMotion6()
        @see MPU6050_RA_ACCEL_XOUT_H
        '''
        ax = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_XOUT_H,2))

        return ax

    def getAccelerationY(self) :
        '''!
        Get Y-axis accelerometer reading.
        @return Y-axis acceleration measurement in 16-bit 2's complement format
        @see getMotion6()
        @see MPU6050_RA_ACCEL_YOUT_H
        '''
        ay = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_YOUT_H,2))

        return ay

    def getAccelerationZ(self) :
        '''!
        Get Z-axis accelerometer reading.
        @return Z-axis acceleration measurement in 16-bit 2's complement format
        @see getMotion6()
        @see MPU6050_RA_ACCEL_ZOUT_H
        '''
        az = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_ACCEL_ZOUT_H,2))

        return az

    # TEMP_OUT_* registers

    def getTemperature(self) :
        '''!
        Get current internal temperature.
        @return Temperature reading in 16-bit 2's complement format
        @see MPU6050_RA_TEMP_OUT_H
        '''
        temp = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_TEMP_OUT_H,2))

        if self.debug:
            print("Raw temperature value: {:d}".format(temp))
        temp = temp/340 + 36.53
        if self.debug:
            print("temperature: {:6.3f}".format(temp))
        return temp
    
    # GYRO_*OUT_* registers

    def getRotation(self) :
        '''!
        Get 3-axis gyroscope readings.
        These gyroscope measurement registers, along with the accelerometer
        measurement registers, temperature measurement registers, and external sensor
        data registers, are composed of two sets of registers: an internal register
        set and a user-facing read register set.
        The data within the gyroscope sensors' internal register set is always
        updated at the Sample Rate. Meanwhile, the user-facing read register set
        duplicates the internal register set's data values whenever the serial
        interface is idle. This guarantees that a burst read of sensor registers will
        read measurements from the same sampling instant. Note that if burst reads
        are not used, the user is responsible for ensuring a set of single byte reads
        correspond to a single sampling instant by checking the Data Ready interrupt.

        Each 16-bit gyroscope measurement has a full scale defined in FS_SEL
        (Register 27). For each full scale setting, the gyroscopes' sensitivity per
        LSB in GYRO_xOUT is shown in the table below:

        <pre>
        FS_SEL | Full Scale Range   | LSB Sensitivity
        -------+--------------------+----------------
        0      | +/- 250 degrees/s  | 131 LSB/deg/s
        1      | +/- 500 degrees/s  | 65.5 LSB/deg/s
        2      | +/- 1000 degrees/s | 32.8 LSB/deg/s
        3      | +/- 2000 degrees/s | 16.4 LSB/deg/s
        </pre>

        @param x 16-bit signed integer container for X-axis rotation
        @param y 16-bit signed integer container for Y-axis rotation
        @param z 16-bit signed integer container for Z-axis rotation
        @see getMotion6()
        @see MPU6050_RA_GYRO_XOUT_H
        '''
        gx = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_GYRO_XOUT_H,2))
        gy = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_GYRO_YOUT_H,2))
        gz = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_GYRO_ZOUT_H,2))

        return(gx,gy,gz)

    def getRotationX(self) :
        '''!
        Get X-axis gyroscope reading.
        @return X-axis rotation measurement in 16-bit 2's complement format
        @see getMotion6()
        @see MPU6050_RA_GYRO_XOUT_H
        '''
        gx = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_GYRO_XOUT_H,2))

        return gx
                            
    def getRotationY(self) :
        '''!
        Get Y-axis gyroscope reading.
        @return Y-axis rotation measurement in 16-bit 2's complement format
        @see getMotion6()
        @see MPU6050_RA_GYRO_YOUT_H
        '''
        gy = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_GYRO_YOUT_H,2))

        return gy

    def getRotationZ(self) :
        '''!
        Get Z-axis gyroscope reading.
        @return Z-axis rotation measurement in 16-bit 2's complement format
        @see getMotion6()
        @see MPU6050_RA_GYRO_YOUT_H
        '''
        gz = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_GYRO_ZOUT_H,2))

        return gz

    # EXT_SENS_DATA_* registers

    def getExternalSensorByte(self,position) :
        '''!
        Read single byte from external sensor data register.
        These registers store data read from external sensors by the Slave 0, 1, 2,
        and 3 on the auxiliary I2C interface. Data read by Slave 4 is stored in
        I2C_SLV4_DI (Register 53).

        External sensor data is written to these registers at the Sample Rate as
        defined in Register 25. This access rate can be reduced by using the Slave
        Delay Enable registers (Register 103).

        External sensor data registers, along with the gyroscope measurement
        registers, accelerometer measurement registers, and temperature measurement
        registers, are composed of two sets of registers: an internal register set
        and a user-facing read register set.

        The data within the external sensors' internal register set is always updated
        at the Sample Rate (or the reduced access rate) whenever the serial interface
        is idle. This guarantees that a burst read of sensor registers will read
        measurements from the same sampling instant. Note that if burst reads are not
        used, the user is responsible for ensuring a set of single byte reads
        correspond to a single sampling instant by checking the Data Ready interrupt.

        Data is placed in these external sensor data registers according to
        I2C_SLV0_CTRL, I2C_SLV1_CTRL, I2C_SLV2_CTRL, and I2C_SLV3_CTRL (Registers 39,
        42, 45, and 48). When more than zero bytes are read (I2C_SLVx_LEN > 0) from
        an enabled slave (I2C_SLVx_EN = 1), the slave is read at the Sample Rate (as
        defined in Register 25) or delayed rate (if specified in Register 52 and
        103). During each Sample cycle, slave reads are performed in order of Slave
        number. If all slaves are enabled with more than zero bytes to be read, the
        order will be Slave 0, followed by Slave 1, Slave 2, and Slave 3.

        Each enabled slave will have EXT_SENS_DATA registers associated with it by
        number of bytes read (I2C_SLVx_LEN) in order of slave number, starting from
        EXT_SENS_DATA_00. Note that this means enabling or disabling a slave may
        change the higher numbered slaves' associated registers. Furthermore, if
        fewer total bytes are being read from the external sensors as a result of
        such a change, then the data remaining in the registers which no longer have
        an associated slave device (i.e. high numbered registers) will remain in
        these previously allocated registers unless reset.

        If the sum of the read lengths of all SLVx transactions exceed the number of
        available EXT_SENS_DATA registers, the excess bytes will be dropped. There
        are 24 EXT_SENS_DATA registers and hence the total read lengths between all
        the slaves cannot be greater than 24 or some bytes will be lost.

        Note: Slave 4's behavior is distinct from that of Slaves 0-3. For further
        information regarding the characteristics of Slave 4, please refer to
        Registers 49 to 53.

        EXAMPLE:
        Suppose that Slave 0 is enabled with 4 bytes to be read (I2C_SLV0_EN = 1 and
        I2C_SLV0_LEN = 4) while Slave 1 is enabled with 2 bytes to be read so that
        I2C_SLV1_EN = 1 and I2C_SLV1_LEN = 2. In such a situation, EXT_SENS_DATA _00
        through _03 will be associated with Slave 0, while EXT_SENS_DATA _04 and 05
        will be associated with Slave 1. If Slave 2 is enabled as well, registers
        starting from EXT_SENS_DATA_06 will be allocated to Slave 2.

        If Slave 2 is disabled while Slave 3 is enabled in this same situation, then
        registers starting from EXT_SENS_DATA_06 will be allocated to Slave 3
        instead.

        REGISTER ALLOCATION FOR DYNAMIC DISABLE VS. NORMAL DISABLE:
        If a slave is disabled at any time, the space initially allocated to the
        slave in the EXT_SENS_DATA register, will remain associated with that slave.
        This is to avoid dynamic adjustment of the register allocation.

        The allocation of the EXT_SENS_DATA registers is recomputed only when (1) all
        slaves are disabled, or (2) the I2C_MST_RST bit is set (Register 106).

        This above is also true if one of the slaves gets NACKed and stops
        functioning.

        @param position Starting position (0-23)
        @return Byte read from register
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_EXT_SENS_DATA_00 + position,1)[0]
    

    def getExternalSensorWord(self,position) :
        '''!
        Read word (2 bytes) from external sensor data registers.
        @param position Starting position (0-21)
        @return Word read from register
        @see getExternalSensorByte()
        '''
        return self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_EXT_SENS_DATA_00 + position,2))

    def getExternalSensorDWord(self,position) :
        '''!
        Read double word (4 bytes) from external sensor data registers.
        @param position Starting position (0-20)
        @return Double word read from registers
        @see getExternalSensorByte()
        '''
        return self.bytesToDoubleInt(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_EXT_SENS_DATA_00 + position,4))

    # MOT_DETECT_STATUS register
    
    def getMotionStatus(self) :
        '''!
        Get full motion detection status register content (all bits).
        @return Motion detection status byte
        @see MPU6050_RA_MOT_DETECT_STATUS
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_MOT_DETECT_STATUS,1)[0]

    def getXNegMotionDetected(self) :
        '''!
        Get X-axis negative motion detection interrupt status.
        @return Motion detection status
        @see MPU6050_RA_MOT_DETECT_STATUS
        @see MPU6050_MOTION_MOT_XNEG_BIT
        '''
        return self.readBit(MPU6050_RA_MOT_DETECT_STATUS, MPU6050_MOTION_MOT_XNEG_BIT)

    def getXPosMotionDetected(self) :
        '''!
        Get X-axis positive motion detection interrupt status.
        @return Motion detection status
        @see MPU6050_RA_MOT_DETECT_STATUS
        @see MPU6050_MOTION_MOT_XPOS_BIT
        '''
        return self.readBit(MPU6050_RA_MOT_DETECT_STATUS, MPU6050_MOTION_MOT_XPOS_BIT)

    def getYNegMotionDetected(self) :
        '''!
        Get Y-axis negative motion detection interrupt status.
        @return Motion detection status
        @see MPU6050_RA_MOT_DETECT_STATUS
        @see MPU6050_MOTION_MOT_YNEG_BIT
        '''
        return self.readBit(MPU6050_RA_MOT_DETECT_STATUS, MPU6050_MOTION_MOT_YNEG_BIT)

    def getYPosMotionDetected(self) :
        '''!
        Get Y-axis positive motion detection interrupt status.
        @return Motion detection status
        @see MPU6050_RA_MOT_DETECT_STATUS
        @see MPU6050_MOTION_MOT_YPOS_BIT
        '''
        return self.readBit(MPU6050_RA_MOT_DETECT_STATUS, MPU6050_MOTION_MOT_YPOS_BIT)

    def getZNegMotionDetected(self) :
        '''!
        Get Z-axis negative motion detection interrupt status.
        @return Motion detection status
        @see MPU6050_RA_MOT_DETECT_STATUS
        @see MPU6050_MOTION_MOT_ZNEG_BIT
        '''
        return self.readBit(MPU6050_RA_MOT_DETECT_STATUS, MPU6050_MOTION_MOT_ZNEG_BIT)

    def getZPosMotionDetected(self) :
        '''!
        Get Z-axis positive motion detection interrupt status.
        @return Motion detection status
        @see MPU6050_RA_MOT_DETECT_STATUS
        @see MPU6050_MOTION_MOT_ZPOS_BIT
        '''
        return self.readBit(MPU6050_RA_MOT_DETECT_STATUS, MPU6050_MOTION_MOT_ZPOS_BIT)

    def getZeroMotionDetected(self) :
        '''!
        Get zero motion detection interrupt status.
        @return Motion detection status
        @see MPU6050_RA_MOT_DETECT_STATUS
        @see MPU6050_MOTION_MOT_ZRMOT_BIT
        '''
        return self.readBit(MPU6050_RA_MOT_DETECT_STATUS, MPU6050_MOTION_MOT_ZRMOT_BIT)

    # I2C_SLV*_DO register
    
    def setSlaveOutputByte(self,num,data) :
        '''!
        Write byte to Data Output container for specified slave.
        This register holds the output data written into Slave when Slave is set to
        write mode. For further information regarding Slave control, please
        refer to Registers 37 to 39 and immediately following.
        @param num Slave number (0-3)
        @param data Byte to write
        @see MPU6050_RA_I2C_SLV0_DO
        '''

        if (num > 3) :
            return
        tmp = bytearray(1)
        tmp[0] = data
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_I2C_SLV0_DO + num, tmp)       

    # I2C_MST_DELAY_CTRL register

    def getExternalShadowDelayEnabled(self) :
        '''!
        Get external data shadow delay enabled status.
        This register is used to specify the timing of external sensor data
        shadowing. When DELAY_ES_SHADOW is set to 1, shadowing of external
        sensor data is delayed until all data has been received.
        @return Current external data shadow delay enabled status.
        @see MPU6050_RA_I2C_MST_DELAY_CTRL
        @see MPU6050_DELAYCTRL_DELAY_ES_SHADOW_BIT
        '''
        return self.readBit(MPU6050_RA_I2C_MST_DELAY_CTRL, MPU6050_DELAYCTRL_DELAY_ES_SHADOW_BIT)

    def setExternalShadowDelayEnabled(self,enabled) :
        '''!
        Set external data shadow delay enabled status.
        @param enabled New external data shadow delay enabled status.
        @see getExternalShadowDelayEnabled()
        @see MPU6050_RA_I2C_MST_DELAY_CTRL
        @see MPU6050_DELAYCTRL_DELAY_ES_SHADOW_BIT
        '''
        self.writeBit(MPU6050_RA_I2C_MST_DELAY_CTRL, MPU6050_DELAYCTRL_DELAY_ES_SHADOW_BIT, enabled)

    def getSlaveDelayEnabled(self,num) :
        '''!
        Get slave delay enabled status.
        When a particular slave delay is enabled, the rate of access for the that
        slave device is reduced. When a slave's access rate is decreased relative to
        the Sample Rate, the slave is accessed every:

            1 / (1 + I2C_MST_DLY) Samples

        This base Sample Rate in turn is determined by SMPLRT_DIV (register  * 25)
        and DLPF_CFG (register 26).

        For further information regarding I2C_MST_DLY, please refer to register 52.
        For further information regarding the Sample Rate, please refer to register 25.

        @param num Slave number (0-4)
        @return Current slave delay enabled status.
        @see MPU6050_RA_I2C_MST_DELAY_CTRL
        @see MPU6050_DELAYCTRL_I2C_SLV0_DLY_EN_BIT
        '''

        # MPU6050_DELAYCTRL_I2C_SLV4_DLY_EN_BIT is 4, SLV3 is 3, etc.
        if (num > 4) :
            return 0
        return self.readBit(MPU6050_RA_I2C_MST_DELAY_CTRL, num)

    def setSlaveDelayEnabled(self,num,enabled) :
        '''!
        Set slave delay enabled status.
        @param num Slave number (0-4)
        @param enabled New slave delay enabled status.
        @see MPU6050_RA_I2C_MST_DELAY_CTRL
        @see MPU6050_DELAYCTRL_I2C_SLV0_DLY_EN_BIT
        '''
        self.writeBit(MPU6050_RA_I2C_MST_DELAY_CTRL, num, enabled)

    # SIGNAL_PATH_RESET register

    def resetGyroscopePath(self) :
        '''!
        Reset gyroscope signal path.
        The reset will revert the signal path analog to digital converters and
        filters to their power up configurations.
        @see MPU6050_RA_SIGNAL_PATH_RESET
        @see MPU6050_PATHRESET_GYRO_RESET_BIT
        '''
        self.writeBit(MPU6050_RA_SIGNAL_PATH_RESET, MPU6050_PATHRESET_GYRO_RESET_BIT,True)

    def resetAccelerometerPath(self) :
        '''!
        Reset accelerometer signal path.
        The reset will revert the signal path analog to digital converters and
        filters to their power up configurations.
        @see MPU6050_RA_SIGNAL_PATH_RESET
        @see MPU6050_PATHRESET_ACCEL_RESET_BIT
        '''
        self.writeBit(MPU6050_RA_SIGNAL_PATH_RESET, MPU6050_PATHRESET_ACCEL_RESET_BIT,True)

    def resetTemperaturePath(self) :
        '''!
        Reset temperature sensor signal path.
        The reset will revert the signal path analog to digital converters and
        filters to their power up configurations.
        @see MPU6050_RA_SIGNAL_PATH_RESET
        @see MPU6050_PATHRESET_TEMP_RESET_BIT
        '''
        self.writeBit(MPU6050_RA_SIGNAL_PATH_RESET, MPU6050_PATHRESET_TEMP_RESET_BIT, True)
        
    # MOT_DETECT_CTRL register

    def getAccelerometerPowerOnDelay(self) :
        '''!
        Get accelerometer power-on delay.
        The accelerometer data path provides samples to the sensor registers, Motion
        detection, Zero Motion detection, and Free Fall detection modules. The
        signal path contains filters which must be flushed on wake-up with new
        samples before the detection modules begin operations. The default wake-up
        delay, of 4ms can be lengthened by up to 3ms. This additional delay is
        specified in ACCEL_ON_DELAY in units of 1 LSB = 1 ms. The user may select
        any value above zero unless instructed otherwise by InvenSense. Please refer
        to Section 8 of the MPU-6000/MPU-6050 Product Specification document for
        further information regarding the detection modules.
        @return Current accelerometer power-on delay
        @see MPU6050_RA_MOT_DETECT_CTRL
        @see MPU6050_DETECT_ACCEL_ON_DELAY_BIT
        '''
        return self.readBits(MPU6050_RA_MOT_DETECT_CTRL, MPU6050_DETECT_ACCEL_ON_DELAY_BIT, MPU6050_DETECT_ACCEL_ON_DELAY_LENGTH)

    def setAccelerometerPowerOnDelay(self,delay) :
        '''!
        Set accelerometer power-on delay.
        @param delay New accelerometer power-on delay (0-3)
        @see getAccelerometerPowerOnDelay()
        @see MPU6050_RA_MOT_DETECT_CTRL
        @see MPU6050_DETECT_ACCEL_ON_DELAY_BIT
        '''
        self.writeBits(MPU6050_RA_MOT_DETECT_CTRL, MPU6050_DETECT_ACCEL_ON_DELAY_BIT, MPU6050_DETECT_ACCEL_ON_DELAY_LENGTH, delay)

    def getFreefallDetectionCounterDecrement(self) :
        '''!
        Get Free Fall detection counter decrement configuration.
        Detection is registered by the Free Fall detection module after accelerometer
        measurements meet their respective threshold conditions over a specified
        number of samples. When the threshold conditions are met, the corresponding
        detection counter increments by 1. The user may control the rate at which the
        detection counter decrements when the threshold condition is not met by
        configuring FF_COUNT. The decrement rate can be set according to the
        following table:

        <pre>
        FF_COUNT | Counter Decrement
        ---------+------------------
        0        | Reset
        1        | 1
        2        | 2
        3        | 4
        </pre>

        When FF_COUNT is configured to 0 (reset), any non-qualifying sample will
        reset the counter to 0. For further information on Free Fall detection,
        please refer to Registers 29 to 32.

        @return Current decrement configuration
        @see MPU6050_RA_MOT_DETECT_CTRL
        @see MPU6050_DETECT_FF_COUNT_BIT
        '''
        return self.readBits(MPU6050_RA_MOT_DETECT_CTRL, MPU6050_DETECT_FF_COUNT_BIT, MPU6050_DETECT_FF_COUNT_LENGTH)

    def setFreefallDetectionCounterDecrement(self,decrement) :
        '''!
        Set Free Fall detection counter decrement configuration.
        @param decrement New decrement configuration value
        @see getFreefallDetectionCounterDecrement()
        @see MPU6050_RA_MOT_DETECT_CTRL
        @see MPU6050_DETECT_FF_COUNT_BIT
        '''
        self.writeBits(MPU6050_RA_MOT_DETECT_CTRL, MPU6050_DETECT_FF_COUNT_BIT, MPU6050_DETECT_FF_COUNT_LENGTH, decrement)

    def getMotionDetectionCounterDecrement(self) :
        '''!
        Get Motion detection counter decrement configuration.
         Detection is registered by the Motion detection module after accelerometer
         measurements meet their respective threshold conditions over a specified
         number of samples. When the threshold conditions are met, the corresponding
         detection counter increments by 1. The user may control the rate at which the
         detection counter decrements when the threshold condition is not met by
         configuring MOT_COUNT. The decrement rate can be set according to the
         following table:

         <pre>
         MOT_COUNT | Counter Decrement
         ----------+------------------
         0         | Reset
         1         | 1
         2         | 2
         3         | 4
         </pre>

         When MOT_COUNT is configured to 0 (reset), any non-qualifying sample will
         reset the counter to 0. For further information on Motion detection,
         please refer to Registers 29 to 32.
        '''
        return self.readBits(MPU6050_RA_MOT_DETECT_CTRL, MPU6050_DETECT_MOT_COUNT_BIT, MPU6050_DETECT_MOT_COUNT_LENGTH)

    def setMotionDetectionCounterDecrement(self,decrement) :
        '''
        Set Motion detection counter decrement configuration.
        @param decrement New decrement configuration value
        @see getMotionDetectionCounterDecrement()
        @see MPU6050_RA_MOT_DETECT_CTRL
        @see MPU6050_DETECT_MOT_COUNT_BIT
        '''
        self.writeBits(MPU6050_RA_MOT_DETECT_CTRL, MPU6050_DETECT_MOT_COUNT_BIT, MPU6050_DETECT_MOT_COUNT_LENGTH, decrement)

    # EXT_SENS_DATA_* registers

    def getExternalSensorByte(self,position) :
        '''!
        Read single byte from external sensor data register.
        These registers store data read from external sensors by the Slave 0, 1, 2,
        and 3 on the auxiliary I2C interface. Data read by Slave 4 is stored in
        I2C_SLV4_DI (Register 53).

        External sensor data is written to these registers at the Sample Rate as
        defined in Register 25. This access rate can be reduced by using the Slave
        Delay Enable registers (Register 103).

        External sensor data registers, along with the gyroscope measurement
        registers, accelerometer measurement registers, and temperature measurement
        registers, are composed of two sets of registers: an internal register set
        and a user-facing read register set.

        The data within the external sensors' internal register set is always updated
        at the Sample Rate (or the reduced access rate) whenever the serial interface
        is idle. This guarantees that a burst read of sensor registers will read
        measurements from the same sampling instant. Note that if burst reads are not
        used, the user is responsible for ensuring a set of single byte reads
        correspond to a single sampling instant by checking the Data Ready interrupt.

        Data is placed in these external sensor data registers according to
        I2C_SLV0_CTRL, I2C_SLV1_CTRL, I2C_SLV2_CTRL, and I2C_SLV3_CTRL (Registers 39,
        42, 45, and 48). When more than zero bytes are read (I2C_SLVx_LEN > 0) from
        an enabled slave (I2C_SLVx_EN = 1), the slave is read at the Sample Rate (as
        defined in Register 25) or delayed rate (if specified in Register 52 and
        103). During each Sample cycle, slave reads are performed in order of Slave
        number. If all slaves are enabled with more than zero bytes to be read, the
        order will be Slave 0, followed by Slave 1, Slave 2, and Slave 3.

        Each enabled slave will have EXT_SENS_DATA registers associated with it by
        number of bytes read (I2C_SLVx_LEN) in order of slave number, starting from
        EXT_SENS_DATA_00. Note that this means enabling or disabling a slave may
        change the higher numbered slaves' associated registers. Furthermore, if
        fewer total bytes are being read from the external sensors as a result of
        such a change, then the data remaining in the registers which no longer have
        an associated slave device (i.e. high numbered registers) will remain in
        these previously allocated registers unless reset.

        If the sum of the read lengths of all SLVx transactions exceed the number of
        available EXT_SENS_DATA registers, the excess bytes will be dropped. There
        are 24 EXT_SENS_DATA registers and hence the total read lengths between all
        the slaves cannot be greater than 24 or some bytes will be lost.

        Note: Slave 4's behavior is distinct from that of Slaves 0-3. For further
        information regarding the characteristics of Slave 4, please refer to
        Registers 49 to 53.

        EXAMPLE:
        Suppose that Slave 0 is enabled with 4 bytes to be read (I2C_SLV0_EN = 1 and
        I2C_SLV0_LEN = 4) while Slave 1 is enabled with 2 bytes to be read so that
        I2C_SLV1_EN = 1 and I2C_SLV1_LEN = 2. In such a situation, EXT_SENS_DATA _00
        through _03 will be associated with Slave 0, while EXT_SENS_DATA _04 and 05
        will be associated with Slave 1. If Slave 2 is enabled as well, registers
        starting from EXT_SENS_DATA_06 will be allocated to Slave 2.

        If Slave 2 is disabled while Slave 3 is enabled in this same situation, then
        registers starting from EXT_SENS_DATA_06 will be allocated to Slave 3
        instead.

        REGISTER ALLOCATION FOR DYNAMIC DISABLE VS. NORMAL DISABLE:
        If a slave is disabled at any time, the space initially allocated to the
        slave in the EXT_SENS_DATA register, will remain associated with that slave.
        This is to avoid dynamic adjustment of the register allocation.

        The allocation of the EXT_SENS_DATA registers is recomputed only when (1) all
        slaves are disabled, or (2) the I2C_MST_RST bit is set (Register 106).

        This above is also true if one of the slaves gets NACKed and stops
        functioning.

        @param position Starting position (0-23)
        @return Byte read from register
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_EXT_SENS_DATA_00 + position,1)[0]


    # USER_CTRL register

    def getFIFOEnabled(self) :
        '''!
        Get FIFO enabled status.
        When this bit is set to 0, the FIFO buffer is disabled. The FIFO buffer
        cannot be written to or read from while disabled. The FIFO buffer's state
        does not change unless the MPU-60X0 is power cycled.
        @return Current FIFO enabled status
        @see MPU6050_RA_USER_CTRL
        @see MPU6050_USERCTRL_FIFO_EN_BIT
        '''
        return self.readBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_EN_BIT)

    def setFIFOEnabled(self,enabled) :
        '''!
        Set FIFO enabled status.
        @param enabled New FIFO enabled status
        @see getFIFOEnabled()
        @see MPU6050_RA_USER_CTRL
        @see MPU6050_USERCTRL_FIFO_EN_BIT
        '''
        self.writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_EN_BIT, enabled)

    def getI2CMasterModeEnabled(self) :
        '''!
        Get I2C Master Mode enabled status.
        When this mode is enabled, the MPU-60X0 acts as the I2C Master to the
        external sensor slave devices on the auxiliary I2C bus. When this bit is
        cleared to 0, the auxiliary I2C bus lines (AUX_DA and AUX_CL) are logically
        driven by the primary I2C bus (SDA and SCL). This is a precondition to
        enabling Bypass Mode. For further information regarding Bypass Mode, please
        refer to Register 55.
        @return Current I2C Master Mode enabled status
        @see MPU6050_RA_USER_CTRL
        @see MPU6050_USERCTRL_I2C_MST_EN_BIT
        '''
        return self.readBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_I2C_MST_EN_BIT)

    
    def setI2CMasterModeEnabled(self,enabled) :
        '''!
        Set I2C Master Mode enabled status.
        @param enabled New I2C Master Mode enabled status
        @see getI2CMasterModeEnabled()
        @see MPU6050_RA_USER_CTRL
        @see MPU6050_USERCTRL_I2C_MST_EN_BIT
        '''
        self.writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_I2C_MST_EN_BIT, enabled)

    def switchSPIEnabled(self,enabled) :
        '''!
        Switch from I2C to SPI mode (MPU-6000 only)
        If this is set, the primary SPI interface will be enabled in place of the
        disabled primary I2C interface.
        '''
        writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_I2C_IF_DIS_BIT, enabled)

    def resetFIFO(self) :
        '''!
        Reset the FIFO.
        This bit resets the FIFO buffer when set to 1 while FIFO_EN equals 0. This
        bit automatically clears to 0 after the reset has been triggered.
        @see MPU6050_RA_USER_CTRL
        @see MPU6050_USERCTRL_FIFO_RESET_BIT
        '''
        self.writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_RESET_BIT, True)

    def resetI2CMaster(self) :
        '''!
        Reset the I2C Master.
        This bit resets the I2C Master when set to 1 while I2C_MST_EN equals 0.
        This bit automatically clears to 0 after the reset has been triggered.
        @see MPU6050_RA_USER_CTRL
        @see MPU6050_USERCTRL_I2C_MST_RESET_BIT
        '''
        self.writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_I2C_MST_RESET_BIT, True)

    def resetSensors() :
        '''!
        Reset all sensor registers and signal paths.
        When set to 1, this bit resets the signal paths for all sensors (gyroscopes,
        accelerometers, and temperature sensor). This operation will also clear the
        sensor registers. This bit automatically clears to 0 after the reset has been
        triggered.

        When resetting only the signal path (and not the sensor registers), please
        use Register 104, SIGNAL_PATH_RESET.

        @see MPU6050_RA_USER_CTRL
        @see MPU6050_USERCTRL_SIG_COND_RESET_BIT
        '''
        self.writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_SIG_COND_RESET_BIT, True)

    # PWR_MGMT_1 register
    def reset(self) :
        '''!
        Trigger a full device reset.
        A small delay of ~50ms may be desirable after triggering a reset.
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_DEVICE_RESET_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_DEVICE_RESET_BIT, True)

    def getSleepEnabled(self) :
        '''!
        Get sleep mode status.
        Setting the SLEEP bit in the register puts the device into very low power
        sleep mode. In this mode, only the serial interface and internal registers
        remain active, allowing for a very low standby current. Clearing this bit
        puts the device back into normal mode. To save power, the individual standby
        selections for each of the gyros should be used if any gyro axis is not used
        by the application.
        @return Current sleep mode enabled status
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_SLEEP_BIT
        '''
        return self.readBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_SLEEP_BIT)

    def setSleepEnabled(self,enabled) :
        '''!
        Set sleep mode status.
        @param enabled New sleep mode enabled status
        @see getSleepEnabled()
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_SLEEP_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_SLEEP_BIT, enabled)

    def getWakeCycleEnabled(self) :
        '''!
        Get wake cycle enabled status.
        When this bit is set to 1 and SLEEP is disabled, the MPU-60X0 will cycle
        between sleep mode and waking up to take a single sample of data from active
        sensors at a rate determined by LP_WAKE_CTRL (register 108).
        @return Current sleep mode enabled status
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_CYCLE_BIT
        '''
        return self.readBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CYCLE_BIT)

    def setWakeCycleEnabled(self,enabled) :
        '''!
        Set wake cycle enabled status.
        @param enabled New sleep mode enabled status
        @see getWakeCycleEnabled()
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_CYCLE_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CYCLE_BIT, enabled)

    def getTempSensorEnabled(self) :
        '''!
        Get temperature sensor enabled status.
        Control the usage of the internal temperature sensor.
 
        Note: this register stores the *disabled* value, but for consistency with the
        rest of the code, the function is named and used with standard true/false
        values to indicate whether the sensor is enabled or disabled, respectively.
 
        @return Current temperature sensor enabled status
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_TEMP_DIS_BIT
        '''
        return not self.readBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_TEMP_DIS_BIT) # return not disabled


    def setTempSensorEnabled(self,enabled) :
        '''!
        Set temperature sensor enabled status.
        Note: this register stores the *disabled* value, but for consistency with the
        rest of the code, the function is named and used with standard true/false
        values to indicate whether the sensor is enabled or disabled, respectively.
 
        @param enabled New temperature sensor enabled status
        @see getTempSensorEnabled()
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_TEMP_DIS_BIT

        # 1 is actually disabled here
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_TEMP_DIS_BIT, not enabled)

    def getClockSource(self) :
        '''!
        Get clock source setting.
        @return Current clock source setting
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_CLKSEL_BIT
        @see MPU6050_PWR1_CLKSEL_LENGTH
        '''

        return self.readBits(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CLKSEL_BIT, MPU6050_PWR1_CLKSEL_LENGTH)

    def setClockSource(self,source) :
        '''!
        Set clock source setting.
        An internal 8MHz oscillator, gyroscope based clock, or external sources can
        be selected as the MPU-60X0 clock source. When the internal 8 MHz oscillator
        or an external source is chosen as the clock source, the MPU-60X0 can operate
        in low power modes with the gyroscopes disabled.

        Upon power up, the MPU-60X0 clock source defaults to the internal oscillator.
        However, it is highly recommended that the device be configured to use one of
        the gyroscopes (or an external clock source) as the clock reference for
        improved stability. The clock source can be selected according to the following table:

        <pre>
        CLK_SEL | Clock Source
        --------+--------------------------------------
        0       | Internal oscillator
        1       | PLL with X Gyro reference
        2       | PLL with Y Gyro reference
        3       | PLL with Z Gyro reference
        4       | PLL with external 32.768kHz reference
        5       | PLL with external 19.2MHz reference
        6       | Reserved
        7       | Stops the clock and keeps the timing generator in reset
        </pre>

        @param source New clock source setting
        @see getClockSource()
        @see MPU6050_RA_PWR_MGMT_1
        @see MPU6050_PWR1_CLKSEL_BIT
        @see MPU6050_PWR1_CLKSEL_LENGTH
        '''
        self.writeBits(MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CLKSEL_BIT, MPU6050_PWR1_CLKSEL_LENGTH, source)

    # PWR_MGMT_2 register

    def getWakeFrequency(self) :
        '''!
        Get wake frequency in Accel-Only Low Power Mode.
        The MPU-60X0 can be put into Accerlerometer Only Low Power Mode by setting
        PWRSEL to 1 in the Power Management 1 register (Register 107). In this mode,
        the device will power off all devices except for the primary I2C interface,
        waking only the accelerometer at fixed intervals to take a single
        measurement. The frequency of wake-ups can be configured with LP_WAKE_CTRL
        as shown below:

        <pre>
        LP_WAKE_CTRL | Wake-up Frequency
        -------------+------------------
        0            | 1.25 Hz
        1            | 2.5 Hz
        2            | 20 Hz
        3            | 40 Hz
        </pre>

        For further information regarding the MPU-60X0's power modes, please refer to
        Register 107.

        @return Current wake frequency
        @see MPU6050_RA_PWR_MGMT_2
        '''
        return self.readBits(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_LP_WAKE_CTRL_BIT, MPU6050_PWR2_LP_WAKE_CTRL_LENGTH)

    def setWakeFrequency(self,frequency) :
        '''!
        Set wake frequency in Accel-Only Low Power Mode.
        @param frequency New wake frequency
        @see MPU6050_RA_PWR_MGMT_2
        '''
        self.writeBits(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_LP_WAKE_CTRL_BIT, MPU6050_PWR2_LP_WAKE_CTRL_LENGTH, frequency)

    def getStandbyXAccelEnabled(self) :
        '''!
        Get X-axis accelerometer standby enabled status.
        If enabled, the X-axis will not gather or report data (or use power).
        @return Current X-axis standby enabled status
        *@see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_XA_BIT
        '''
        return self.readBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_XA_BIT)

    def setStandbyXAccelEnabled(self,enabled) :
        '''!
        Set X-axis accelerometer standby enabled status.
        @param New X-axis standby enabled status
        @see getStandbyXAccelEnabled()
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_XA_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_XA_BIT, enabled)

    def getStandbyYAccelEnabled(self) :
        '''!
        Get Y-axis accelerometer standby enabled status.
        If enabled, the Y-axis will not gather or report data (or use power).
        @return Current Y-axis standby enabled status
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_YA_BIT
        '''
        return self.readBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_YA_BIT)

    def setStandbyYAccelEnabled(self,enabled) :
        '''!
        Set Y-axis accelerometer standby enabled status.
        @param New Y-axis standby enabled status
        @see getStandbyYAccelEnabled()
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_YA_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_YA_BIT, enabled)

    def standbyZAccelEnabled(self) :
        '''!
        Get Z-axis accelerometer standby enabled status.
        If enabled, the Z-axis will not gather or report data (or use power).
        @return Current Z-axis standby enabled status
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_ZA_BIT
        '''
        return self.readBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_ZA_BIT)

    def setStandbyZAccelEnabled(self,enabled) :
        '''!
        Set Z-axis accelerometer standby enabled status.
        @param New Z-axis standby enabled status
        @see getStandbyZAccelEnabled()
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_ZA_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_ZA_BIT, enabled)
        
    def getStandbyXGyroEnabled(self) :
        '''!
        Get X-axis gyroscope standby enabled status.
        If enabled, the X-axis will not gather or report data (or use power). 
        @return Current X-axis standby enabled status
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_XG_BIT
        '''
        return self.readBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_XG_BIT)

    def setStandbyXGyroEnabled(self,enabled) :
        '''!
        Set X-axis gyroscope standby enabled status.
        @param New X-axis standby enabled status
        @see getStandbyXGyroEnabled()
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_XG_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_XG_BIT, enabled)

    def getStandbyYGyroEnabled(self) :
        '''!
        Get Y-axis gyroscope standby enabled status.
        If enabled, the Y-axis will not gather or report data (or use power).
        @return Current Y-axis standby enabled status
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_YG_BIT
        '''
        return self.readBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_YG_BIT)

    def setStandbyYGyroEnabled(self,enabled) :
        '''!
        Set Y-axis gyroscope standby enabled status.
        @param New Y-axis standby enabled status
        @see getStandbyYGyroEnabled()
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_YG_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_YG_BIT, enabled)

    def getStandbyZGyroEnabled(self) :
        '''!
        Get Z-axis gyroscope standby enabled status.
        If enabled, the Z-axis will not gather or report data (or use power).
        @return Current Z-axis standby enabled status
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_ZG_BIT
        '''
        return self.readBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_ZG_BIT)

    def setStandbyZGyroEnabled(self,enabled) :
        '''!
        Set Z-axis gyroscope standby enabled status.
        @param New Z-axis standby enabled status
        @see getStandbyZGyroEnabled()
        @see MPU6050_RA_PWR_MGMT_2
        @see MPU6050_PWR2_STBY_ZG_BIT
        '''
        self.writeBit(MPU6050_RA_PWR_MGMT_2, MPU6050_PWR2_STBY_ZG_BIT, enabled)

    # FIFO_COUNT* registers

    def getFIFOCount(self) :
        '''!
        Get current FIFO buffer size.
        This value indicates the number of bytes stored in the FIFO buffer. This
        number is in turn the number of bytes that can be read from the FIFO buffer
        and it is directly proportional to the number of samples available given the
        set of sensor data bound to be stored in the FIFO (register 35 and 36).
        @return Current FIFO buffer size
        '''
        return self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_FIFO_COUNTH,2))

    # FIFO_R_W register

    def getFIFOByte(self) :
        '''!
        Get byte from FIFO buffer.
        This register is used to read and write data from the FIFO buffer. Data is
        written to the FIFO in order of register number (from lowest to highest). If
        all the FIFO enable flags (see below) are enabled and all External Sensor
        Data registers (Registers 73 to 96) are associated with a Slave device, the
        contents of registers 59 through 96 will be written in order at the Sample
        Rate.

        The contents of the sensor data registers (Registers 59 to 96) are written
        into the FIFO buffer when their corresponding FIFO enable flags are set to 1
        in FIFO_EN (Register 35). An additional flag for the sensor data registers
        associated with I2C Slave 3 can be found in I2C_MST_CTRL (Register 36).

        If the FIFO buffer has overflowed, the status bit FIFO_OFLOW_INT is
        automatically set to 1. This bit is located in INT_STATUS (Register 58).
        When the FIFO buffer has overflowed, the oldest data will be lost and new
        data will be written to the FIFO.

        If the FIFO buffer is empty, reading this register will return the last byte
        that was previously read from the FIFO until new data is available. The user
        should check FIFO_COUNT to ensure that the FIFO buffer is not read when
        empty.

        @return Byte from FIFO buffer
        '''
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_FIFO_COUNTH,1)[0]

    
    def getFIFOBytes(length) :
        if length > 0:
            return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_FIFO_R_W,length)
        else :
    	    return None

    def getFIFOTimeout(self) :
        '''!
        Get timeout to get a packet from FIFO buffer.
        @return Current timeout to get a packet from FIFO buffer
        @see MPU6050_FIFO_DEFAULT_TIMEOUT
        '''
	return self.fifoTimeout;

    def setFIFOTimeout(self,fifoTimeout) :
        '''!
        Set timeout to get a packet from FIFO buffer.
        @param New timeout to get a packet from FIFO buffer
        @see MPU6050_FIFO_DEFAULT_TIMEOUT
        '''
	self.fifoTimeout = fifoTimeout

    def GetCurrentFIFOPacket(self, data, length)  : # overflow proof
        '''!
        Get latest byte from FIFO buffer no matter how much time has passed.
        ===                  GetCurrentFIFOPacket                    ===
        ================================================================
        Returns 1) when nothing special was done
        2) when recovering from overflow
        0) when no valid data is available
        ================================================================ 
        '''

        # This section of code is for when we allowed more than 1 packet to be acquired
        BreakTimer = time();
        packetReceived = False;
        fifoc = self.getFIFOCount()
        while True:
            fifoC = self.getFIFOCount()
            if fifoC > 200: # if you waited to get the FIFO buffer to > 200 bytes
                            # it will take longer to get the last packet
                            # in the FIFO Buffer than it will take
                            # to  reset the buffer and wait for the next to arrive
                self.resetFIFO()  # Fixes any overflow corruption
                fifoC = 0
                while True:
                    fifoC = self.getFIFOCount()
                    if fifoC and time() - BreakTimer <= self.getFIFOTimeout() :
                        pass  # Get Next New Packet
                    else :        # We have more than 1 packet but less than 200 bytes of data in the FIFO Buffer
                        while True:
                            fifoC = self.getFIFOCount()
                            if fifoC > length :            # Test each time just in case the MPU is writing to the FIFO Buffer
                                fifoC = fifoC - length     # Save the last packet
                            # uint16_t  RemoveBytes;
                        while (fifoC) : # fifo count will reach zero so this is safe
                            # Buffer Length is different than the packet length this will efficiently clear the buffer
                            if fifoC < I2CDEVLIB_WIRE_BUFFER_LENGTH :
                                RemoveBytes = fifoC
                            else :
                                RemoveBytes = I2CDEVLIB_WIRE_BUFFER_LENGTH
                            
                            Trash = getFIFOBytes(RemoveBytes)
                            fifoC -= RemoveBytes
                return 2,None
            
            if not fifoC :
                return 0,None  # Called too early no data or we timed out after FIFO Reset
            # We have 1 packet
            if fifoC == length:
                packetReceived = True
            else :
                packetReceived = False
            if packetReceived and time() - BreakTimer > self.getFIFOTimeout():
                return 0,None
            if packetReceived:
                data = self.getFIFOBytes(length)
                return 1,data

    def setFIFOByte(self,data) :
        '''!
        Write byte to FIFO buffer.
        @see getFIFOByte()
        @see MPU6050_RA_FIFO_R_W
        '''
        tmp = bytearray(1)
        tmp[0] = data
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_FIFO_R_W, tmp)       


    # ======== UNDOCUMENTED/DMP REGISTERS/METHODS ========

    # XG_OFFS_TC register

    def  getOTPBankValid(self) :
        return slef.readBit(MPU6050_RA_XG_OFFS_TC, MPU6050_TC_OTP_BNK_VLD_BIT)

    def setOTPBankValid(sel,enabled) :
        self.writeBit(MPU6050_RA_XG_OFFS_TC, MPU6050_TC_OTP_BNK_VLD_BIT, enabled)

    def getXGyroOffsetTC(self) :
        return self.readBits(MPU6050_RA_XG_OFFS_TC, MPU6050_TC_OFFSET_BIT, MPU6050_TC_OFFSET_LENGTH)

    def setXGyroOffsetTC(self,offset) :
        self.writeBits(MPU6050_RA_XG_OFFS_TC, MPU6050_TC_OFFSET_BIT, MPU6050_TC_OFFSET_LENGTH, offset)



    # YG_OFFS_TC register

    def getYGyroOffsetTC(self) :
        return self.readBits(MPU6050_RA_YG_OFFS_TC, MPU6050_TC_OFFSET_BIT, MPU6050_TC_OFFSET_LENGTH)

    def setYGyroOffsetTC(self,offset) :
        self.writeBits(MPU6050_RA_YG_OFFS_TC, MPU6050_TC_OFFSET_BIT, MPU6050_TC_OFFSET_LENGTH)


    # ZG_OFFS_TC register

    def getZGyroOffsetTC(self) :
        return self.readBits(MPU6050_RA_ZG_OFFS_TC, MPU6050_TC_OFFSET_BIT, MPU6050_TC_OFFSET_LENGTH)

    def setZGyroOffsetTC(self,offset) :
        self.writeBits(MPU6050_RA_ZG_OFFS_TC, MPU6050_TC_OFFSET_BIT, MPU6050_TC_OFFSET_LENGTH)


    # X_FINE_GAIN register

    def getXFineGain(self) :
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_X_FINE_GAIN,1)[0]

    def setXFineGain(self,gain) :
        tmp = bytearray(1)
        tmp[0] = gain
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_X_FINE_GAIN, tmp)       

    # Y_FINE_GAIN register

    def getYFineGain(self) :
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_Y_FINE_GAIN,1)[0]

    def setYFineGain(self,gain) :
        tmp = bytearray(1)
        tmp[0] = gain
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_Y_FINE_GAIN, tmp)       

    # Z_FINE_GAIN register

    def getZFineGain(self) :
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_Z_FINE_GAIN,1)[0]

    def setZFineGain(self,gain) :
        tmp[0] = gain
        self.i2c.writeto_mem(self.mpu6050_address,MPU6050_RA_Z_FINE_GAIN, tmp)       

    # XA_OFFS_* registers
    
    def getXAccelOffset(self) :
        if self.getDeviceID() < 0x38:
            SaveAddress = MPU6050_RA_XA_OFFS_H
        else:
            SaveAddress = 0x77
        return self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, SaveAddress,2))

    def setXAccelOffset(self,offset) :
        tmp = self.intToBytes(offset)
        if self.getDeviceID() < 0x38:
            SaveAddress = MPU6050_RA_XA_OFFS_H # MPU6050,MPU9150 Vs MPU6500,MPU9250
        else:
            SaveAddress = 0x77
        self.i2c.writeto_mem(self.mpu6050_address,SaveAddress, tmp)

    # YA_OFFS_* registers
    
    def getYAccelOffset(self) :
        if self.getDeviceID() < 0x38:
            SaveAddress = MPU6050_RA_YA_OFFS_H # MPU6050,MPU9150 Vs MPU6500,MPU9250
        else:
            SaveAddress = 0x7a
        return self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, SaveAddress,2))

    def setYAccelOffset(self,offset) :
        tmp = self.intToBytes(offset)
        if self.getDeviceID() < 0x38:
            SaveAddress = MPU6050_RA_YA_OFFS_H # MPU6050,MPU9150 Vs MPU6500,MPU9250
        else:
            SaveAddress = 0x7a
        self.i2c.writeto_mem(self.mpu6050_address,SaveAddress, tmp)

    # ZA_OFFS_* register
    
    def getZAccelOffset(self) :
        if self.getDeviceID() < 0x38:
            SaveAddress = MPU6050_RA_ZA_OFFS_H # MPU6050,MPU9150 Vs MPU6500,MPU9250
        else:
            SaveAddress = 0x7d
        return self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, SaveAddress,2))

    def setZAccelOffset(self,offset) :
        tmp = self.intToBytes(offset)
        if self.getDeviceID() < 0x38:
            SaveAddress = MPU6050_RA_ZA_OFFS_H # MPU6050,MPU9150 Vs MPU6500,MPU9250
        else:
            SaveAddress = 0x7d
        self.i2c.writeto_mem(self.mpu6050_address,SaveAddress, tmp)
        
    # XG_OFFS_USR* registers

    def getXGyroOffset(self) :
        return self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_XG_OFFS_USRH ,2))

    def setXGyroOffset(self,offset) :
        tmp = self.intToBytes(offset)
        self.i2c.writeto_mem(self.mpu6050_address, MPU6050_RA_XG_OFFS_USRH, tmp)

    # YG_OFFS_USR* register

    def getYGyroOffset(self) :
        return self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_YG_OFFS_USRH ,2))

    def setYGyroOffset(self,offset) :
        tmp = self.intToBytes(offset)
        self.i2c.writeto_mem(self.mpu6050_address, MPU6050_RA_YG_OFFS_USRH, tmp)

    # ZG_OFFS_USR* register
    
    def getZGyroOffset(self) :
        return self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_ZG_OFFS_USRH ,2))

    def setZGyroOffset(self,offset) :
        tmp = self.intToBytes(offset)
        self.i2c.writeto_mem(self.mpu6050_address, MPU6050_RA_ZG_OFFS_USRH, tmp)

    # INT_ENABLE register (DMP functions)

    def getIntPLLReadyEnabled(self) :
        return self.readBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_PLL_RDY_INT_BIT)

    def setIntPLLReadyEnabled(self,enabled) :
        self.writeBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_PLL_RDY_INT_BIT)

    def getIntDMPEnabled(self) :
        return self.readBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_DMP_INT_BIT)

    def setIntDMPEnabled(self,enabled) :
        self.writeBit(MPU6050_RA_INT_ENABLE, MPU6050_INTERRUPT_DMP_INT_BIT, enabled)

    # DMP_INT_STATUS

    def getDMPInt5Status(self) :
        self.readBit(MPU6050_RA_DMP_INT_STATUS, MPU6050_DMPINT_5_BIT)

    def getDMPInt4Status(self) :
        return self.readBit(MPU6050_RA_DMP_INT_STATUS, MPU6050_DMPINT_4_BIT)

    def getDMPInt3Status(self) :
        return self.readBit(MPU6050_RA_DMP_INT_STATUS, MPU6050_DMPINT_3_BIT)

    def getDMPInt2Status(self) :
        return self.readBit(MPU6050_RA_DMP_INT_STATUS, MPU6050_DMPINT_2_BIT)

    def getDMPInt1Status(self) :
        return self.readBit(MPU6050_RA_DMP_INT_STATUS, MPU6050_DMPINT_1_BIT)

    def getDMPInt0Status(self) :
        return self.readBit(MPU6050_RA_DMP_INT_STATUS, MPU6050_DMPINT_0_BIT)

    # INT_STATUS register (DMP functions)

    def getIntPLLReadyStatus(self) :
        return self.readBit(MPU6050_RA_INT_STATUS, MPU6050_INTERRUPT_PLL_RDY_INT_BIT)

    def getIntDMPStatus(self) :
        return self.readBit(MPU6050_RA_INT_STATUS, MPU6050_INTERRUPT_DMP_INT_BIT)

    # USER_CTRL register (DMP functions)

    def getDMPEnabled(self) :
        return self.readBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_DMP_EN_BIT)

    def setDMPEnabled(self,enabled) :
        self.writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_DMP_EN_BIT, enabled)

    def resetDMP(self) :
        self.writeBit(MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_DMP_RESET_BIT, True)


    # BANK_SEL register

    def setMemoryBank(self,bank, prefetchEnabled, userBank) :
        bank &= 0x1F
        if userBank:
            bank |= 0x20
        if prefetchEnabled:
            bank |= 0x40
        tmp = bytearray(1)
        tmp[0] = bank
        self.i2c.writeto_mem(self.mpu6050_address, MPU6050_RA_BANK_SEL, tmp)

    # MEM_START_ADDR register

    def setMemoryStartAddress(self,address) :
        tmp = bytearray(1)
        tmp[0]= adress
        self.i2c.writeto_mem(self.mpu6050_address,  MPU6050_RA_MEM_START_ADDR, tmp)


    # MEM_R_W register

    def readMemoryByte(self) :
        return self.i2c.readfrom_mem(self.mpu6050_address,  MPU6050_RA_MEM_R_W,1)[0]  

    def writeMemoryByte(self,data) :
        tmp = bytearray(1)
        tmp[0]=data
        self.i2c.writeto_mem(self.mpu6050_address, MPU6050_RA_MEM_R_W, tmp)

    def readMemoryBlock(self,dataSize, bank, address) :
        self.setMemoryBank(bank)
        self.setMemoryStartAddress(address)

        for i in range(dataSize):
            # determine correct chunk size according to bank position and data size
            data = bytearray()
            chunkSize = MPU6050_DMP_MEMORY_CHUNK_SIZE
            
            # make sure we don't go past the data size
            if i + chunkSize > dataSize :
                chunkSize = dataSize - i
                
                # make sure this chunk doesn't go past the bank boundary (256 bytes)
                if chunkSize > 256 - address :
                    chunkSize = 256 - address;
                    
                # read the chunk of data as specified
                chunk = bytearray(self.i2c.readfrom_mem(self.mpu6050_address,MPU6050_RA_MEM_R_W,chunkSize))
                # append the chunk to data
                data.extend(chunk)
                # I2Cdev::readBytes(devAddr, MPU6050_RA_MEM_R_W, chunkSize, data + i, I2Cdev::readTimeout, wireObj);
                
                # increase byte index by [chunkSize]
                i += chunkSize
                
                # uint8_t automatically wraps to 0 at 256
                address += chunkSize & 0xff
                
                # if we aren't done, update bank (if necessary) and address
                if i < dataSize :
                    if address == 0 :
                        bank += 1
                self.setMemoryBank(bank)
                self.setMemoryStartAddress(address)
        return data
    
    def writeMemoryBlock(data, dataSize, bank, address, verify, useProgMem) :
        self.setMemoryBank(bank)
        self.setMemoryStartAddress(address)
        
        if (verify) :
            verifyBuffer = bytearray(MPU6050_DMP_MEMORY_CHUNK_SIZE)

        if (useProgMem) :
            progBuffer = bytearray(MPU6050_DMP_MEMORY_CHUNK_SIZE)
            
        for i in range(dataSize) :
            # determine correct chunk size according to bank position and data size
            chunkSize = MPU6050_DMP_MEMORY_CHUNK_SIZE

        # make sure we don't go past the data size
        if i + chunkSize > dataSize:
            chunkSize = dataSize - i

        # make sure this chunk doesn't go past the bank boundary (256 bytes)
        if chunkSize > 256 - address :
            chunkSize = 256 - address
        
        if useProgMem :
            # write the chunk of data as specified
            for j in range(chunkSize) :
                progBuffer[j] = self.pgm_read_byte(data + i + j)
        else :
            # write the chunk of data as specified
            progBuffer = data + i

        self.i2c.writeto_mem(self.mpu6050_address, MPU6050_RA_MEM_R_W, chunksize)
            # I2Cdev::writeBytes(devAddr, MPU6050_RA_MEM_R_W, chunkSize, progBuffer, wireObj);

        # verify data if needed
        if verify and verifyBuffer :
            self.setMemoryBank(bank)
            self.setMemoryStartAddress(address)
            verifyBuffer = self.i2c.readfrom_mem(self.mpu6050_address,  MPU6050_RA_MEM_R_W,chunksize)
            # I2Cdev::readBytes(devAddr, MPU6050_RA_MEM_R_W, chunkSize, verifyBuffer, I2Cdev::readTimeout, wireObj);
            if progBuffer != verifyBuffer:
                print("Block write verification error, bank {:d}, address {:d} !".format(bank,address))
                print("Expected:",end='');
                for j in range(chunkSize):
                    if progBuffer[j] < 0: 
                        print(" 0x00 ",end='')
                    else :
                        print(" 0x{:02x} ".format(progBuffer[j]),end='')
                print("\nReceived:",end='')
                for j in range(chunkSize):
                    if verifyBuffer[j] < 0: 
                        print(" 0x00 ",end='')
                    else :
                        print(" 0x{:02x} ".format(verifyBuffer[j]),end='')
                print("")
                return False # uh oh.

        # increase byte index by [chunkSize]
        i += chunkSize

        # uint8_t automatically wraps to 0 at 256
        address += chunkSize & 0xff

        # if we aren't done, update bank (if necessary) and address
        if i < dataSize:
            if address == 0:
                bank +=1
            self.setMemoryBank(bank);
            self.setMemoryStartAddress(address)
        return True

    def writeProgMemoryBlock(data, dataSize, bank, address, verify) :
        return self.writeMemoryBlock(data, dataSize, bank, address, verify, True)

    def writeDMPConfigurationSet(data, dataSize, useProgMem) :
        if useProgMem:
            progBuffer = bytearray(8) # assume 8-byte blocks, realloc later if necessary

        # config set data is a long string of blocks with the following structure:
        # [bank] [offset] [length] [byte[0], byte[1], ..., byte[length]]

        for i in range(dataSize):
            if useProgMem:
                bank = self.pgm_read_byte(data + i)
                i += 1
                offset = self.pgm_read_byte(data + i)
                i+=1
                length = self.pgm_read_byte(data + i)
                i += 1
            else :
                bank = data[i]
                i += 1
                offset = data[i]
                i += 1
                length = data[i]
                i += 1

        # write data or perform special action
        if length > 0 :
            # regular block of data to write
            if self.debug:
                print("Writing config block to bank 0x{:02x}, offset 0x{:02x}, length 0x{:02x}".format(bank,offset,length))
            if useProgMem:
                if len(progBuffer) < length:
                      progBuffer = bytearray(length)
                for j in range(length):
                      progBuffer[j] = self.pgm_read_byte(data + i + j)
            else :
                progBuffer = progbuffer[i:]

            success = self.writeMemoryBlock(progBuffer, length, bank, offset, True)
            i += length
        else :
            # special instruction
            # NOTE: this kind of behavior (what and when to do certain things)
            # is totally undocumented. This code is in here based on observed
            # behavior only, and exactly why (or even whether) it has to be here
            # is anybody's guess for now.
            if useProgMem:
                special = self.pgm_read_byte(data)    
            else :
                special = data[i]
                i += 1
            if self.debug:
                print("Special command code 0x{:02x} found".format(special))

            if special == 0x01:
                # enable DMP-related interrupts
                
                self.setIntZeroMotionEnabled(True)
                self.setIntFIFOBufferOverflowEnabled(True)
                # setIntDMPEnabled(true);
                tmp = bytearray(1)
                tmp[0] = 0x32
                self.i2c.writeto_mem(self.mpu6050_address,  MPU6050_RA_INT_ENABLE, tmp, 1)
                success = True;
            else :
                # unknown special command
                success = False
        if not success :
            return False  #  uh oh

        return True

    def writeProgDMPConfigurationSet(data, dataSize):
        return self.writeDMPConfigurationSet(data, dataSize, True)

    # DMP_CFG_1 register

    def getDMPConfig1() :
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_DMP_CFG_1, 1)[0]

    def setDMPConfig1(config) :
        tmp = bytearray(1)
        tmp[0]=config
        self.i2c.writeto_mem(self.mpu6050_address, MPU6050_RA_DMP_CFG_1, tmp, 1)

    # DMP_CFG_2 register

    def getDMPConfig2() :
        return self.i2c.readfrom_mem(self.mpu6050_address, MPU6050_RA_DMP_CFG_2, 1)[0]

    def setDMPConfig2(config) :
        tmp = bytearray(1)
        tmp[0]=config
        self.i2c.writeto_mem(self.mpu6050_address, MPU6050_RA_DMP_CFG_2, tmp, 1)

    #***************************************************************************************
    #**********************           Calibration Routines            **********************
    #***************************************************************************************

    def map(self,value,fromLow,fromHigh,toLow,toHigh):
        '''!
        implements the Arduino map function which maps a number from one range to another
        @ return the number mapped into the output range
        '''
        return (value-fromLow) * (toHigh - toLow) // (fromHigh - fromLow) + toLow
    

    '''!
    @brief      Fully calibrate Gyro from ZERO in about 6-7 Loops 600-700 readings
    '''
    def CalibrateGyro(self,Loops) :
        kP = 0.3
        kI = 90.0
        x = (100 - self.map(Loops, 1, 5, 20, 0)) * .01
        kP *= x
        kI *= x
  
        self.PID( 0x43,  kP, kI,  Loops)

    '''!
    @brief Fully calibrate Accel from ZERO in about 6-7 Loops 600-700 readings
    '''
    def CalibrateAccel(self,Loops) :

	kP = 0.3
	kI = 20
	x = (100 - self.map(Loops, 1, 5, 20, 0)) * .01
	kP *= x
	kI *= x
	self.PID( 0x3B, kP, kI,  Loops) 

    def PID(self,ReadAddress, kP, kI, Loops):
        ITerm = [None]*3
        
        if ReadAddress == 0x3B:
            if self.getDeviceID() < 0x38:
                SaveAddress = 0x06
            else:
                SaveAddress = 0x77
        else:
            SaveAddress = 0x13
            
        BitZero = [None]*3    
        if SaveAddress == 0x77:
            shift = 3
        else:
            shift = 2

	gravity = 8192 # prevent uninitialized compiler warning
	if ReadAddress == 0x3B :
            gravity = 16384 >> self.getFullScaleAccelRange()
	print('>',end='')
        for i in range(3):
            Data = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, SaveAddress + (i * shift) ,2)) # reads a 16 bit integers (Word)
	    Reading = Data
	    if SaveAddress != 0x13:
	        BitZero[i] = Data & 1									      # Capture Bit Zero to properly handle Accelerometer calibration
		ITerm[i] = Reading * 8.0
	    else :
		ITerm[i] = Reading * 4.0
	for int in range(Loops):
	    eSample = 0
            for c in range(100): # 100 pi Calculations
	        eSum = 0
                for i in range(3) :
                    Data = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, ReadAddress + (i * 2), 2)) # reads a 16 bit integers (Word)
		    Reading = Data
		    # if ReadAddress == 0x3B and i == 2:
                    if ReadAddress == 0x3B and i == 0:  # my mpu6050 is mounted vertically
                        Reading -= gravity	        # remove Gravity
		    Error = -Reading
		    eSum += abs(Reading)
		    PTerm = kP * Error
		    ITerm[i] += (Error * 0.001) * kI				# Integral term 1000 Calculations a second = 0.001
		    if SaveAddress != 0x13 :
			Data = round((PTerm + ITerm[i] ) / 8)		        # Compute PID Output
			Data = (Data & 0xFFFE) | BitZero[i]			        # Insert Bit0 Saved at beginning
		    else :
                        Data = round((PTerm + ITerm[i] ) / 4)	                # Compute PID Output
                        
                    tmp = self.intToBytes(Data)
                    self.i2c.writeto_mem(self.mpu6050_address, SaveAddress + (i * shift), tmp)

		    if c == 99 and eSum > 1000 :				# Error is still to great to continue 
			c = 0
			print('*',end='')

                    if ReadAddress == 0x3B:
                        tmp = 0.5
                    else:
                        tmp = 1
                    if eSum * tmp < 5:
                        eSample += 1
		    # if((eSum * ((ReadAddress == 0x3B)?.05: 1)) < 5):
                    #     eSample++;	// Successfully found offsets prepare to  advance

		    if eSum < 100 and c > 10 and eSample >= 10 :
                        break		#Advance to next Loop
		    sleep_ms(1)

	    print('.',end='')
	    kP *= .75
	    kI *= .75
            for i in range(3):
		if SaveAddress != 0x13 :
		    Data = round((ITerm[i] ) / 8)		# Compute PID Output
		    Data = (Data & 0xFFFE) |BitZero[i]	# Insert Bit0 Saved at beginning
		else :
                    Data = round((ITerm[i]) / 4)
                    tmp = self.intToBytes(Data)
                    self.i2c.writeto_mem(self.mpu6050_address, SaveAddress + (i * shift), tmp)

	self.resetFIFO()
	self.resetDMP()

    def PrintActiveOffsets(self) :
        if self.getDeviceID() < 0x38 :    
	    AOffsetRegister = MPU6050_RA_XA_OFFS_H
        else :
            AOffsetRegister = 0x77
	Data = [None]*3
	# print("Offset Register 0x{:04x}".format(AOffsetRegister>>4))
	# print(AOffsetRegister&0x0F,HEX);
	print("\n   X Accel  Y Accel  Z Accel   X Gyro   Y Gyro   Z Gyro      OFFSETS ")
	if AOffsetRegister == 0x06 :
            Data[0] = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, AOffsetRegister, 2)) # reads a 16 bit integers (Word)
            Data[1] = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, AOffsetRegister+2, 2)) # reads a 16 bit integers (Word)
            Data[2] = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, AOffsetRegister+4, 2)) # reads a 16 bit integers (Word)

	    # I2Cdev::readWords(devAddr, AOffsetRegister, 3, (uint16_t *)Data, I2Cdev::readTimeout, wireObj);
	else :
            Data[0] = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, AOffsetRegister, 2)) # reads a 16 bit integers (Word)
            Data[1] = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, AOffsetRegister+3, 2)) # reads a 16 bit integers (Word)
            Data[2] = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, AOffsetRegister+6, 2)) # reads a 16 bit integers (Word)
	    # I2Cdev::readWords(devAddr, AOffsetRegister, 1, (uint16_t *)Data, I2Cdev::readTimeout, wireObj);
	    # I2Cdev::readWords(devAddr, AOffsetRegister+3, 1, (uint16_t *)Data+1, I2Cdev::readTimeout, wireObj);
	    # I2Cdev::readWords(devAddr, AOffsetRegister+6, 1, (uint16_t *)Data+2, I2Cdev::readTimeout, wireObj);

        print("    {:5d},   ".format(int(Data[0])),end='')
        print("{:5d},   ".format(int(Data[1])),end='')
        print("{:5d},   ".format(int(Data[2])),end='')
        for i in range(3):
            Data[i] = self.bytesToInt(self.i2c.readfrom_mem(self.mpu6050_address, 0x13 + 2*i, 2)) # reads a 16 bit integers (Word)
	    # I2Cdev::readWords(devAddr, 0x13, 3, (uint16_t *)Data, I2Cdev::readTimeout, wireObj);
            # XG_OFFSET_H_READ_OFFS_USR(Data);
        print("{:5d},   ".format(int(Data[0])),end='')
        print("{:5d},   ".format(int(Data[1])),end='')
        print("{:5d},   ".format(int(Data[2])))


