from machine import Pin,DAC
from time import sleep_ms

dac = DAC(Pin(26))
print("Running a squarewave")
level = 0
while True:
    dac.write(level)
    if level == 0:
        level = 255
    else:
        level = 0
    sleep_ms(1)

    
