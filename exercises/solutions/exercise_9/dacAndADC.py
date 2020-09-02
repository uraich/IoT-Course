'''
    Send the value 0..256 to the DAC and read the analogue value 
    back on the ADC
    Copyright (c) U. Raich 2020
    This program is part of the course on IoT at
    the University of Cape Coast, Ghana
''' 
from machine import Pin, ADC, DAC
from time import sleep_ms

adc = ADC(Pin(36))  # create ADC object on ADC pin
adc.atten(ADC.ATTN_11DB)
dac = DAC(Pin(26))

file= open("linearity.dat","w")
print("Send values from 0 ..255 to DAC and read the signal level back on the ADC")
print("The ADC values are saved in the file 'linearity.dat'")
for i in range(256):
    # send the value to the DAC and wait for 50 ms to stabilize
    # then read back the signal level on the DAC
    dac.write(i)
    sleep_ms(50)
    file.write("{:d}\n".format(adc.read()))
for i in range(255):
    dac.write(254-i)
    sleep_ms(50)
    file.write("{:d}\n".format(adc.read()))    
file.close()
