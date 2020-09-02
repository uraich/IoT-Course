# reads the analogue value from the slider potentiometer connected to the ADC
# on pin 36 marked A0 on the ESP32 CPU board
# Copyright U. Raich 2020
# The program is part of the IoT course at the University of Cape Coast, Ghana

from machine import Pin, ADC
from time import sleep

slider = ADC(Pin(36))  # create ADC object on ADC pin 36
slider.atten(ADC.ATTN_11DB)

while True:
    print("Slider: ",slider.read())
    sleep(0.5)
