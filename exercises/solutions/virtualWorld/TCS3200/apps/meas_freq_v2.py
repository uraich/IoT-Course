# meas_freq.py: We want to get a feeling for the frequencies emitted by the TCS3200
# Here we finally start our first measurement.
# An interrupt service routine is added to the driver which is triggered on the rising edge of the OUT signal.
# The filters are set to clear and the frequency divider to 2%. We measure the time it takes to see 10 rising edges
# A new method is added to allow setting of the number of OUT cycles for which the time is measured
#
# Copyright (c) U. Raich
# Written for the course on the Internet of Things at the
# University of Cape Coast, Ghana
# The program is released under the MIT licence

from tcs3200_v2 import TCS3200
from utime import sleep_ms

# create an TCS3200 object
tcs3200 = TCS3200(OUT=19, S2=5, S3=18, S0=17, S1=16, LED=23)

# set debugging on
tcs3200.debugging=tcs3200.ON

# switch the LEDs on
tcs3200.led = tcs3200.ON

# set the filters to clear and read the settings back
tcs3200.filter=tcs3200.CLEAR
print(tcs3200.filter)
if tcs3200.filter == tcs3200.CLEAR:
    print("Filter is set to CLEAR")
else:
    print("Something went wrong when setting the filter")

# Set the frequency divider to 2% and read it back
tcs3200.freq_divider=tcs3200.TWO_PERCENT
print(tcs3200.freq_divider)
if tcs3200.freq_divider == tcs3200.TWO_PERCENT:
    print("Frequency divider is set to 2%")
else:
    print("Something went wrong when setting the frequency divider")

while True:
    # Start the measurement
    tcs3200.meas()

    while tcs3200._meas:
        sleep_ms(10)
    print("Measurement duration: {:d}".format(tcs3200.meas_duration))
    print("Frequency: {:f} Hz".format(tcs3200.measured_freq))

    sleep_ms(2000)

