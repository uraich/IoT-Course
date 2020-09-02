'''
    Send the value 0..256 to the DAC and read the analogue value 
    back on the ADC
    Copyright (c) U. Raich 2020
    This program is part of the course on IoT at
    the University of Cape Coast, Ghana
''' 
from machine import Pin, ADC, DAC
from time import sleep_ms
import math

adc = ADC(Pin(36))  # create ADC object on ADC pin
adc.atten(ADC.ATTN_11DB)
dac = DAC(Pin(26))
coeff=[5.348296376602186e-17,-1.2714627449190296e-12,6.144261403098308e-09,
       -1.0935276513490784e-05,0.07562048627541001,1.016015679447536]

file= open("corrected.dat","w")
print("Send values from 0 ..255 to DAC and read the signal level back on the ADC")
print("The ADC values are saved in the file 'corrected.dat'")
for i in range(256):
    # send the value to the DAC and wait for 50 ms to stabilize
    # then read back the signal level on the DAC
    dac.write(i)
    value = adc.read()
    corrected = coeff[0]*math.pow(value,5)+coeff[1]*math.pow(value,4)+coeff[2]*math.pow(value,3)+ coeff[3]*math.pow(value,2) +coeff[4]*value + coeff[5]
    sleep_ms(50)
    file.write("{:f}\n".format(corrected*16))
for i in range(255):
    dac.write(254-i)
    sleep_ms(50)
    value = adc.read()
    corrected = coeff[0]*math.pow(value,5)+coeff[1]*math.pow(value,4)+coeff[2]*math.pow(value,3)+ coeff[3]*math.pow(value,2) +coeff[4]*value + coeff[5]
    file.write("{:f}\n".format(corrected*16))    
file.close()
