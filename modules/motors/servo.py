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
        # the SH90 servo motor runs on 50 Hz (20 ms period)
        # the duty cycle runs from 0 .. 1023
        if angle < -90 or angle > 90 :
            print("angles should be in the range -90 .. 90")
            raise Exception("Angles must be in the range 0° .. 90°")
        
        duty = (angle+90)*115/180  + 35 # experimentally found that 35 .. 160
                                        # corresponds to 0 .. 180 degrees
        return int(duty)

    #  angles range from -90° to + 90°
    def angle(self,value):
        dutyCycle = self._angle2DutyCycle(value)
        self.servo.duty(dutyCycle)
