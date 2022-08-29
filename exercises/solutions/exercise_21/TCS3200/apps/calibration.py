# calibration.py: The value for a color component is calculated with the following formula:
# rgb = max * (Fv -Fb) / (Fw -Fb) where
# max is the maximum for each color component. This is generally 0xff or 255
# Fv is the frequency measured to the color component
# Fw is the frequency when measuring a white target
# Fb is the frequency when measuring a black target
# Before measuring the frequency of a color component and calculating the rgb value of a colored target
# we must measure the rgb frequencies for a black and a white target first
# These calibration values are stored in the _freq_black and _freq_white arrays. 
#
# Copyright (c) U. Raich
# Written for the course on the Internet of Things at the
# University of Cape Coast, Ghana
# The program is released under the MIT licence

from tcs3200 import TCS3200

# create an TCS3200 object
tcs3200 = TCS3200(OUT=19, S2=5, S3=18, S0=17, S1=16, LED=23)

# set debugging on
tcs3200.debugging=tcs3200.ON

# switch the LEDs on
tcs3200.led = tcs3200.ON

# Set the frequency divider to 2% and read it back
tcs3200.freq_divider=tcs3200.TWO_PERCENT
print(tcs3200.freq_divider)
if tcs3200.freq_divider == tcs3200.TWO_PERCENT:
    print("Frequency divider is set to 2%")
else:
    print("Something went wrong when setting the frequency divider")

# Set no of cycles to be measured
tcs3200.cycles=100
tcs3200.calibrate()
black_freq = tcs3200.calib(tcs3200.BLACK)
print("Calibration frequencies for black: ",black_freq)
white_freq = tcs3200.calib(tcs3200.WHITE)
print("Calibration frequencies for white: ",white_freq)


