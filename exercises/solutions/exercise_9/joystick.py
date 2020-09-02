from machine import Pin, ADC
from time import sleep

horadc = ADC(Pin(34))  # create ADC object on ADC pin 34
horadc.atten(ADC.ATTN_11DB)
veradc = ADC(Pin(33))  # create ADC object on ADC pin 33
veradc.atten(ADC.ATTN_11DB)
while True:
    print("Horizontal: ",horadc.read())
    print("Vertical: ",veradc.read())
    sleep(1)
