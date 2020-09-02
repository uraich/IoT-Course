from machine import I2C, Pin,DAC
from ads1x15 import ADS1115
import sys,time

if sys.platform == "esp8266":
#    print("Running on ESP8266")
    pinScl      =  5  #ESP8266 GPIO5 (D1
    pinSda      =  4  #ESP8266 GPIO4 (D2)
else:
#    print("Running on ESP32") 
    pinScl      =  22  # SCL on esp32 
    pinSda      =  21  # SDA ON ESP32
    
dac = DAC(Pin(26))
i2c = I2C(1,scl=Pin(pinScl), sda=Pin(pinSda))

file= open("linADS1115.dat","w")
ads1115 = ADS1115(i2c)
for i in range(256):
    dac.write(i)
    value = ads1115.read(1)
    print("DAC value: {:d}, ADC value: {:d}".format(i,value))
    file.write("{:d}\n".format(value))
    time.sleep(0.1)
file.close()
