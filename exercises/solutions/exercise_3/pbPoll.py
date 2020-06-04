# pbPoll: Reads the state of a pushbutton every 100 ms
# Prints state changes
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

oldState = True
try:
    while True:
        state = pushButton.value()
        if state != oldState:
            if state:
                print("Push button was released!")
            else:
                print("Push button was pushed!")
            oldState = state
        time.sleep_ms(100)
                
except KeyboardInterrupt:
    print("Ctrl C seen! Quitting the program")
    sys.exit(0)

 


