# DC motor: The program controls a DC motor using the L298D motor driver
#
# Copyright (c) U. Raich, March 2022
# This program is part of a course on IoT at the
# Université Cheikh Anta Diop, Dakar, Sénégal
# The program is released under the MIT licence
#
# Connections are as follows:
#
# L298D       WeMos ESP32   external 9V battery   motor       comments
#  12V                           + pole
#  GND           GND    and      - pole
#  OUT1                                           + pole
#  OUT2                                           - pole
#  IN1       D1: GPIO 22                                      defines movement
#  IN2       D2: GPIO 21                                      direction
#  EN1       D0: GPIO 26

from machine import Pin,PWM
from utime import sleep,sleep_ms

SPEED = 26
DIR1  = 22
DIR2  = 21
FULL_SPEED = 1023

speed = PWM(Pin(SPEED))

dir1 = Pin(DIR1,Pin.OUT)
dir2 = Pin(DIR2,Pin.OUT)

# Set full speed
speed.duty(FULL_SPEED)

# Now we can start the motor in forward direction
print("Start the motor")
dir2.value(0)
dir1.value(1)
sleep(3)

# stop the motor
print("Stop the motor")
dir1.value(0)
sleep(1)

print("Reverse the movement")
dir2.value(1)
sleep(3)
#
print("Stop the motor")
dir2.value(0)

# Now let's change the speed
speed.duty(0)

# increasing and decreasing motor speed
dir1.value(1)

print("Changing motor speed, forward movement")

for i in range(1024):
    speed.duty(i)
    sleep_ms(10)
sleep(3)
for i in range(1024):
    speed.duty(1023-i)
    sleep_ms(10)

dir1.value(0)
dir2.value(1)

print("Changing motor speed, reverse movement")

for i in range(1024):
    speed.duty(i)
    sleep_ms(10)
sleep(3)
for i in range(1024):
    speed.duty(1023-i)
    sleep_ms(10)

print("Stop the motor and end the program")

dir2.value(0)

