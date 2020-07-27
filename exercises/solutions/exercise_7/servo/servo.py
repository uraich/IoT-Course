#
# Servo.py: a class to control the SG90 servo motor
# Copyright (c) U. Raich, June 2020
# This program is part of the IoT course at the
# University of Cape Coast, Ghana
# Released under GPL

from machine import Pin,PWM
_SERVO_PIN=26 # default signal pin of the servo motor

class Servo:
    def __init__(self,servoPin=26):
        self.servo=PWM(Pin(servoPin))
        self.servo.freq(50) # set PWM to 50 Hz

    def _angle2DutyCycle(self,angle):
        duty = angle*90.0/180.0 + 35.0
        return int(duty)
    
    def angle(self,value):
        dutyCycle = self._angle2DutyCycle(value)
        self.servo.duty(dutyCycle)

