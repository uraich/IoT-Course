from machine import Pin, ADC
from time import sleep

adc = ADC(Pin(34))  # create ADC object on ADC pin
adc.atten(ADC.ATTN_11DB)
while True:
    raw = adc.read()
    voltage = raw*3.3/4096
    print("Voltage: raw: {:04d}".format(raw),end="")
    print(" in Volts: {:.1f}".format(voltage))

    sleep(1)
