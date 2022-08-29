# pulses.py: try to reconstruct the pulses emitted by the shinyei ppd42nj
# We collect the ticks in ms for the falling and rising adges of the P1 and P2
# signals and save these into a data file
# The data file can be transfered to the PC and the signal reconstructed with
# and evaluation program
# Copyright (c) U. Raich, June 2022
# This program is part of the course on the Internet of Things at
# the University of Cape Coast, Ghana

# P1: GPIO 23
# P2: GPIO 19

from machine import Pin
from utime import sleep,sleep_ms,ticks_ms

P1 = 23
P2 = 19

CONVERSION_FACTOR = 1000/283 # the spec sheet uses no of particles in 283 ml

class Shinyei:
    def __init__(self,P1=23,P2=19,debug=False):

        self._p1 = Pin(P1,Pin.IN)
        self._p2 = Pin(P2,Pin.IN)
        self._meas_duration = 30000 # meaasurement duration in ms
        self._debug = debug

    def set_debug(self,onOff):
        self._debug = onOff

    def get_debug(self):
        return self._debug

    def set_meas_duration(self,duration):
        self._meas_duration = duration

    def get_meas_duration(self):
        return self._meas_duration
    
    def edges_P1(self,src):    
        if src.value() :
            self._stops_P1.append(ticks_ms())
        else:
            self._starts_P1.append(ticks_ms())
            
    def edges_P2(self,src) :
        if src.value() :
            self._stops_P2.append(ticks_ms())
        else:
            self._starts_P2.append(ticks_ms())
                        
    def measure(self):
        if self._debug:
            print("Starting measurement for {:5.2f} s".format(
                self._meas_duration/1000))

        self._starts_P1 = []
        self._stops_P1  = []
        self._starts_P2 = []
        self._stops_P2  = []
        
        # start the measurement enabling the interrupts on the rising
        # and falling edges of P1 and P2
        self._p1.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.edges_P1)
        self._p2.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.edges_P2)


        # sleep for the number of ms stored in _meas_duration
        # print a "." every seconds to indicate that something is active
        if self._debug:
            for i in range(self._meas_duration/1000):
                print(".",end="")
                sleep(1)
            if self._meas_duration % 1000:
                sleep_ms(self._meas_duration % 1000)
            print("")
            
        # stop the measurement disabling the interrupts
        self._p1.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = None)
        self._p2.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = None)

    def start_stop_times(self):
        return self._starts_P1,self._stops_P1,self._starts_P2,self._stops_P2

    # from the start and stop times, calculate the low occupancy time
    def lot(self) :        
        self._lot_P1 = 0
        if len(self._starts_P1) == len(self._stops_P1) :
            for i in range(len(self._starts_P1)):
                self._lot_P1 += self._stops_P1[i] - self._starts_P1[i]
        else:
            print("Not equal P1 starts and stops")
            
        self._lot_P2 = 0
        if len(self._starts_P2) == len(self._stops_P2) :
            for i in range(len(self._starts_P2)):
                self._lot_P2 += self._stops_P2[i] - self._starts_P2[i]
        else:
            print("Not equal P2 starts and stops")
        if self._debug:
            print("self._lot_P1: {:d}, self._lot_P2: {:d}".format(self._lot_P1, self._lot_P2))
        return self._lot_P1, self._lot_P2

    def lot_per_cent(self):
        # calculate low occupancy time in %
        lot_P1, lot_P2 = self.lot()
        if lot_P1 == 0:
            lot_P1_percent = 0
        else:
            lot_P1_percent = lot_P1*100/self._meas_duration
            
        if lot_P2 == 0:
            lot_P2_percent = 0
        else:
            lot_P2_percent = lot_P2*100/self._meas_duration
        if self._debug:
            print("lot_P1_percent: {:5.2f}, lot_P2_percent: {:5.2f}".format(
                lot_P1_percent, lot_P2_percent))
        return lot_P1_percent, lot_P2_percent
            
    # calculate the concentration 
    def concentration(self):
        x_P1, x_P2 = self.lot_per_cent() # get the low occupancy numbers
        # fit to the calibration curve from the data sheet
        if self._debug:
            print("x_P1: {:5.2f}, x_P2: {:5.2f}".format(x_P1,x_P2))
        if x_P1 == 0:
            y_P1 = 0.0
        else:
            y_P1 =  1.1*x_P1*x_P1*x_P1 - 3.8*x_P1*x_P1 + 520*x_P1 + 0.62

        if x_P2 == 0:
            y_P2 = 0.0
        else:
            y_P2 =  1.1*x_P2*x_P2*x_P2 - 3.8*x_P2*x_P2 + 520*x_P2 + 0.62
        return y_P1, y_P2
    
shinyei = Shinyei(debug=True)
shinyei.measure()
p1_start, p1_stop, p2_start, p2_stop = shinyei.start_stop_times()

print("No of falling P1 edges: {:d} and rising edges: {:d}".format(
    len(p1_start),len(p1_stop)))

print("No of falling P2 edges: {:d} and rising edges: {:d}".format(
    len(p2_start),len(p2_stop)))

if len(p1_start) == len(p1_stop):
    for i in range(len(p1_start)):
        print("start: {:d}, stop:{:d}".format(p1_start[i],p1_stop[i]))

lot_P1, lot_P2 = shinyei.lot()
print("Low occupance time: P1: {:d} ms, P2: {:d} ms".format(lot_P1,lot_P2))

lot_P1, lot_P2 = shinyei.lot_per_cent()
print("Low occupance time: P1: {:5.2f} %, P2: {:5.2f} %".format(lot_P1,lot_P2))

c_P1,c_P2 = shinyei.concentration()
print("Concentration (Number of particles in 283 ml): P1: {:d}, P2: {:d}".format(
    int(c_P1),int(c_P2)))
