# A simple program to make the DC motor word with the WeMos S1 mini motor shield
# Program written for the IoT course at the University of Cape Coast
# copyright (c) U. Raich June 2020
# This program is released under GPL

from machine import Pin,I2C
from d1motor import Motor
import sys,time

_MOTOR_SHIELD_ADDR = 0x30

if sys.platform == "esp8266":
    print("Running on ESP8266")
    scl = Pin(5)   # on the wemos d1 mini (esp8266) scl is connected to GPIO 5
    sda = Pin(4)   # on the wemos d1 mini (esp8266) sda is connected to GPIO 4
else:
    print("Running on ESP32") 
    scl = Pin(22)   # on the wemos d1 mini (esp32) scl is connected to GPIO 22
    sda = Pin(21)   # on the wemos d1 mini (esp32) sda is connected to GPIO 21

i2c = I2C(-1,scl,sda)
addr = i2c.scan()

if not _MOTOR_SHIELD_ADDR in addr:
    print("Could not find the motor shield on the I2C bus, giving up")
    sys.exit()
else:
    print("Found motor shield, continuing")

motorA = Motor(0,i2c)

# run the motor clock wise in increasing speed
for i in range(1,10):
    motorA.speed(1000*(i+1))
    time.sleep(2)
motorA.brake()
time.sleep(1)

# run the motor clock wise in increasing speed
for i in range(1,10):
    motorA.speed(-1000*(i+1))
    time.sleep(2)
motorA.brake()