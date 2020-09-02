#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License

# For the DAC exercises we use the internal 8 bit DAC of the esp32 

import sys,time
from machine import DAC,Pin

_DAC_MAX_VALUE=255
_DAC_CHANNEL_0 = Pin(25)
_DAC_CHANNEL_1 = Pin(26)

dac = DAC(_DAC_CHANNEL_0)

while True:
    try:
        dac.write(_DAC_MAX_VALUE)
        print("DAC set to max")
        time.sleep(1)
        dac.write(_DAC_MAX_VALUE)
        print("DAC set to zero")
        time.sleep(1)
    except KeyboardInterrupt:
         print("Ctrl C seen! Setting DAC to zero")
         sys.exit(0)
   
          


