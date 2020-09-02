from machine import Pin,DAC
from time import sleep_ms

dac = DAC(Pin(26))
print("Running a triangular wave form with a frequency of ~ 1 Hz on pin 26")
while True:
    for i in range(256):
        dac.write(i)
        sleep_ms(2)
    for i in range(256):
        dac.write(256-i-1)
        sleep_ms(2)
    
