#
# matrix.py a test program for the LED matrix
# a value of 0..64 will light 0 .. 64 LEDs
# written for the workshop on IoT at the
# African Internet Summit 2019, Kampala, Uganda
# Copyright U. Raich
# This program is released under GPL

import ledMatrix.mled
import time,sys

if sys.platform == "esp8266":
    _CLK = 14
    _DIN = 13
else:
    _CLK = 18
    _DIN = 23

class LedMatrix:
    def __init__(self):
        self.matrix=ledMatrix.mled.driver(_DIN,_CLK)
        self.matrix.clear()
        self.matrix.setIntensity(2)
    
    def clear(self):
        self.matrix.clear()

    def setLevel(self,value):
        self.matrix.clear()
        if (value < 0) or (value > 64):
            print("Illegal value")
            return
        y = value // 8
        x = value % 8
        for i in range(0,y):
            for j in range(0,8):
                self.matrix.pixel(j,i,self.matrix.ON)
        for i in range(0,x):
            self.matrix.pixel(i,y,self.matrix.ON)
        self.matrix.display()
    def setIntensity(self,intens):
        if intens < 0 or intens > 7:
            return
        self.matrix.setIntensity(intens);

