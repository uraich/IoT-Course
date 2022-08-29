# timeout.py: This is a copy of meas_freq.py with a timeout counter
# included. 
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

# Set no of cycles to be measured
tcs3200.cycles = 100

for _ in range(2):
    # Start the measurement
    tcs3200.meas=tcs3200.ON
    print("cycle: {:d}, no of cycles: {:d}".format(tcs3200._cycle,tcs3200.cycles))
    try:
        while tcs3200._end_tick == 0:
            time.sleep_ms(10)
    except Exception as e:
        print(e)
        sys.exit(-1)

    print("Start time: {:d}".format(tcs3200._start_tick))
    print("End time: {:d}".format(tcs3200._end_tick))
    print("No of cycles measured: {:d}".format(tcs3200._cycle))
    print("Duration: {:d}us".format(tcs3200._end_tick - tcs3200._start_tick))
    print("Frequency: {:f} Hz".format(tcs3200.measured_freq))
    
    time.sleep(2)
    tcs3200.cycles = 10000 # provoke a timeout

