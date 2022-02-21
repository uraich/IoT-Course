# I2C device class (I2Cdev) demonstration Arduino sketch for MPU6050 class
# 10/7/2011 by Jeff Rowberg <jeff@rowberg.net>
# Updates should (hopefully) always be available at https://github.com/jrowberg/i2cdevlib
#
# Changelog:
#
#      2022-07-02 - ported to MicroPython
#      2013-05-08 - added multiple output formats
#                 - added seamless Fastwire support
#      2011-10-07 - initial release

# ============================================
'''
I2Cdev device library code is placed under the MIT license
Copyright (c) 2011 Jeff Rowberg

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
import sys
from utime import sleep_ms 
from machine import Pin,I2C 
from MPU6050_const import *
from MPU6050 import MPU6050

# class default I2C address is 0x68
# specific I2C addresses may be passed as a parameter here
# AD0 low = 0x68 (default for InvenSense evaluation board)
# AD0 high = 0x69

# MPU6050 accelgyro(0x69); // <-- use for AD0 high
# MPU6050 accelgyro(0x68, &Wire1); // <-- use for AD0 low, but 2nd Wire (TWI/I2C) object

# uncomment "OUTPUT_READABLE_ACCELGYRO" if you want to see a tab-separated
# list of the accel X/Y/Z and then gyro X/Y/Z values in decimal. Easy to read,
# not so easy to parse, and slow(er) over UART.
OUTPUT_READABLE_ACCELGYRO = True

# uncomment "OUTPUT_BINARY_ACCELGYRO" to send all 6 axes of data as 16-bit
# binary, one right after the other. This is very fast (as fast as possible
# without compression or data loss), and easy to parse, but impossible to read
# for a human.
# OUTPUT_BINARY_ACCELGYRO = True

led = Pin(19,Pin.OUT)
blinkState = False

# i2c bus is initialized in the MPU6050 class

# initialize device
print("Initializing I2C devices...");
# accelgyro = MPU6050(debug=True)
accelgyro = MPU6050()

# verify connection
print("Testing device connections...")
if accelgyro.testConnection():
    print("MPU6050 connection successful")
else:
    print("MPU6050 connection failed")
    sys.exit()

# use the code below to change accel/gyro offset values

print("Updating internal sensor offsets...")
#  -76	-2359	1688	0	0	0
print(accelgyro.getXAccelOffset(), end = '')
print("\t",end='') # -76
print(accelgyro.getYAccelOffset(),end='')
print("\t",end='') # -2359
print(accelgyro.getZAccelOffset(),end='')
print("\t",end='') # 1688
print(accelgyro.getXGyroOffset(),end='')
print("\t",end='') # 0
print(accelgyro.getYGyroOffset(),end='')
print("\t",end='') # 0
print(accelgyro.getZGyroOffset(),end='')
print("\t",end='') # 0
print("")
accelgyro.setXAccelOffset(-1082)
accelgyro.setYAccelOffset(-2965)
accelgyro.setZAccelOffset(1256)
accelgyro.setXGyroOffset(76)
accelgyro.setYGyroOffset(39)
accelgyro.setZGyroOffset(12)

print(accelgyro.getXAccelOffset(),end='')
print("\t",end='') # -76
print(accelgyro.getYAccelOffset(),end='')
print("\t",end='') # -2359
print(accelgyro.getZAccelOffset(),end='')
print("\t",end='') # 1688
print(accelgyro.getXGyroOffset(),end='')
print("\t",end='') # 0
print(accelgyro.getYGyroOffset(),end='');
print("\t",end='') # 0
print(accelgyro.getZGyroOffset(),end='');
print("\t",end='') # 0
print("");

while True:
    # read raw accel/gyro measurements from device
    accel_gyro = accelgyro.getMotion6()
    ax = accel_gyro[0]
    ay = accel_gyro[1]
    az = accel_gyro[2]
    gx = accel_gyro[3]
    gy = accel_gyro[4]
    gz = accel_gyro[5]

    # these methods (and a few others) are also available
    # accelgyro.getAcceleration(&ax, &ay, &az);
    # accelgyro.getRotation(&gx, &gy, &gz);

    if OUTPUT_READABLE_ACCELGYRO:
        # display tab-separated accel/gyro x/y/z values
        print("a/g:\t",end="")
        print(ax,end='')
        print("\t",end='')
        print(ay,end='')
        print("\t",end='')
        print(az,end='')
        print("\t",end='')
        print(gx,end='')
        print("\t",end='')
        print(gy,end='')
        print("\t",end='')
        print(gz);

    '''
    if OUTPUT_BINARY_ACCELGYRO:
        Serial.write((uint8_t)(ax >> 8)); Serial.write((uint8_t)(ax & 0xFF));
        Serial.write((uint8_t)(ay >> 8)); Serial.write((uint8_t)(ay & 0xFF));
        Serial.write((uint8_t)(az >> 8)); Serial.write((uint8_t)(az & 0xFF));
        Serial.write((uint8_t)(gx >> 8)); Serial.write((uint8_t)(gx & 0xFF));
        Serial.write((uint8_t)(gy >> 8)); Serial.write((uint8_t)(gy & 0xFF));
        Serial.write((uint8_t)(gz >> 8)); Serial.write((uint8_t)(gz & 0xFF));
    '''    

    # blink LED to indicate activity
    blinkState = not blinkState
    led.value(blinkState)
    sleep_ms(100)


