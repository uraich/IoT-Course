from machine import Pin,DAC
from time import sleep

dac = DAC(Pin(26))
print("Running a triangular wave form with a frequency of ~ 1 Hz on pin 26")
while True:
    dac.write(0)
    sleep(2)
    dac.write(255)
    sleep(2)
    
