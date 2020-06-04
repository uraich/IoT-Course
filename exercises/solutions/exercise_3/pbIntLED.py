# pbIntLED: Works the same way as pbInterrupt but switches the esp32
# builtin LED on and off instead of printing the message
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
_LED_PIN = 2

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
    
 


