# outSignal: We want to get a feeling for the frequencies emitted by the TCS3200
# To measure these we will set the filters to clear and the frequency divider to 2%
# To make this work we need additional methods of the TCS3200 class
# allowing to set (and read back) the filters and the frequency divider
# This version of the driver only adds this additional functionality
# 
# The testOut method reads the OUT signal every 100 us during 100 ms and saves the results in the values list
# The contents of the list can be printed, transfered to the PC using
# ampy run outSignal.py > data.txt
# and plotted using gnuplot
#
# Copyright (c) U. Raich
# Written for the course on the Internet of Things at the
# University of Cape Coast, Ghana
# The program is released under the MIT licence

from tcs3200 import TCS3200
import sys
# create an TCS3200 object
tcs3200 = TCS3200(OUT=19, S2=5, S3=18, S0=17, S1=16, LED=23)

# set debugging on
tcs3200.debugging=tcs3200.OFF

# switch the LEDs on
tcs3200.led = tcs3200.ON

# set the filters to clear and read the settings back
tcs3200.filter=tcs3200.CLEAR
print(tcs3200.filter)
if tcs3200.filter != tcs3200.CLEAR:
    print("Something went wrong when setting the filter")
    sys.exit()
    
# Set the frequency divider to 2% and read it back
tcs3200.freq_divider=tcs3200.TWO_PERCENT
print(tcs3200.freq_divider)
if tcs3200.freq_divider != tcs3200.TWO_PERCENT:
    print("Something went wrong when setting the frequency divider")
    sys.exit()

# start measuring
signalData = tcs3200.testOut()
for i in range(len(signalData)):
    print(signalData[i])
               
