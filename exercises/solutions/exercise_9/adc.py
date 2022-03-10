# reads the analogue value from the slider potentiometer connected to the ADC
# on pin 36 marked A0 on the ESP32 CPU board
# Copyright U. Raich 2020
# The program is part of the IoT course at the University of Cape Coast, Ghana

from machine import Pin, ADC
from time import sleep_ms

slider = ADC(Pin(36),atten=ADC.ATTN_11DB)  # create ADC object on ADC pin 36

while True:
    s12 = slider.read()
    s16 = slider.read_u16()
    smV = slider.read_uv()//1000  # value is in micro Volt with a resolution of 1 milli Volt
    print("Slider 12 bits: in decimal {:d} and in hex 0x{:04x}".format(s12,s12))
    print("Slider 16 bits: in decimal {:d} and in hex 0x{:04x}".format(s16,s16))
    print("Slider in mV: {:d}".format(smV))    
    sleep_ms(500)
