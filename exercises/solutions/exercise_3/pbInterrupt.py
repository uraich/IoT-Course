# pbInterrupt: Reads the state of a pushbutton whenever it changes
# It uses interrupts and a callback routine to accomplish this
# This program was written for the course on IoT at the
# University of Cape Coast, Ghana 
# Copyright (c) U.Raich, May 2020
# The program was released under the GNU Public License

from machine import Pin
import sys,time

print("Testing the push button")
print("Program written for the course on IoT at the")
print("University of Cape Coast, Ghana")
print("Copyright: U.Raich")
print("Released under the Gnu Public License")

_PB_PIN = 17
pushButton = Pin(_PB_PIN,Pin.IN,Pin.PULL_UP)

def stateChange(pb):
    if pb.value:
        print("Switch was released!")
    else:
        print("Switch was pressed!")

pushButton.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=stateChange)
    
 


