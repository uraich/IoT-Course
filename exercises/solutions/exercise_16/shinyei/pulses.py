# pulses.py: try to reconstruct the pulses emitted by the shinyei ppd42nj
# Read P1 every ms and save the state in an array
# Copyright (c) U. Raich, June 2022
# This program is part of the course on the Internet of Things at
# the University of Cape Coast, Ghana

# P1: GPIO 23
# P2: GPIO 19

from machine import Pin
from utime import sleep,sleep_ms,ticks_ms

P1 = 23
P2 = 19

class Shinyei_pulse:
    def __init__(self,P1=23,P2=19,debug=False):

        self._p1 = Pin(P1,Pin.IN)
        self._p2 = Pin(P2,Pin.IN)
        self._meas_duration = 10000 # meaasurement duration in ms
        self._debug = debug

    def get_pulse(self):
        self._pulse = [None]*self._meas_duration
        for i in range(self._meas_duration):
            self._pulse[i] = self._p1.value()
            sleep_ms(1)
        return self._pulse
        
    def results(self):
        return self._starts_P1,self._stops_P1,self._starts_P2,self._stops_P2
        
shinyei = Shinyei_pulse(debug=True)
data = shinyei.get_pulse()
for i in range(len(data)):
    print(data[i])
                     
