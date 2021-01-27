# pbIntLED: Works the same way as pbInterrupt but switches the esp32
# builtin LED on and off instead of printing the message
# This program was written for the course on IoT at the
# University of Cape Coast, Ghana 
# Copyright (c) U.Raich, May 2020
# The program was released under the GNU Public License

from machine import Pin
import sys,time
import os
osVersion=os.uname()

# if there is 'spiram' in the machine name then we are on the T7 V1.4
if osVersion.machine.find('spiram') == -1:
    _LED_PIN = 2
else:
    _LED_PIN = 19
_PB_PIN = 22

print("Testing the push button")
print("Program written for the course on IoT at the")
print("University of Cape Coast, Ghana")
print("Copyright: U.Raich")
print("Released under the Gnu Public License")

pushButton = Pin(_PB_PIN,Pin.IN,Pin.PULL_UP)
led        = Pin(_LED_PIN,Pin.OUT)
led.off()

def stateChange(pb):
    print("state: ",pb.value())
    if pb.value():
        led.off()
    else:
        led.on()

pushButton.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=stateChange)
    
 


