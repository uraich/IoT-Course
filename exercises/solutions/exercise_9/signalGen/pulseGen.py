#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License

# Generates a wave form on the DAC

import sys,time,math

_SAVE_TO_FILE = True
_NO_OF_SAMPLES=100
_DAC_MAX_VALUE=255

if sys.platform == 'linux':
    if len(sys.argv) != 2:
        print("Usage: %s wave type"%ssys.argv[0])
        print("Wave type can be 'sin', 'rect','sawtooth' or 'triangular'")
        sys.exit(-1)
    if sys.argv[1] != "sin" and sys.argv[1] != "rect" and sys.argv[1] != "sawtooth"\
       and sys.argv[1] != "triangular":
        print("Unknown wav type")
        print("Known wave types are 'sin', 'rect','sawtooth' or 'triangular'")
        sys.exit(-1)
    _WAVEFORM = sys.argv[1]
    print("Can only generate wave files for inspection with gnuplot")
else:    
    _WAVEFORM = "sawtooth"

if sys.platform == 'esp32':
    from machine import DAC,Pin
    _DAC_CHANNEL_0 = Pin(25)
    _DAC_CHANNEL_1 = Pin(26)
    dac = DAC(_DAC_CHANNEL_1)

if _WAVEFORM == "sin":
    # create a sine wave
    sine=[]
    waveform=sine
    for i in range(_NO_OF_SAMPLES):
        sine.append((math.sin(2*math.pi*i/_NO_OF_SAMPLES)+1)*_DAC_MAX_VALUE/2);
    if _SAVE_TO_FILE:
        fd = open("sineWave.txt","w")
        for i in range(_NO_OF_SAMPLES):
            fd.write(str(sine[i]))
            fd.write("\n ")
        fd.close

if _WAVEFORM == "rect":
    # create rectangular wave form
    rect = []
    waveform=rect
    for i in range(_NO_OF_SAMPLES//2): 
        rect.append(0)
    for i in range(_NO_OF_SAMPLES//2): 
        rect.append(_DAC_MAX_VALUE)
        
    if _SAVE_TO_FILE:
        fd = open("rectWave.txt","w")
        for i in range(_NO_OF_SAMPLES):
            fd.write(str(rect[i]))
            fd.write("\n ")
        fd.close

if _WAVEFORM == "sawtooth":
    # create sawtooth wave form
    sawtooth = []
    waveform=sawtooth
    for i in range(_NO_OF_SAMPLES): 
        sawtooth.append(_DAC_MAX_VALUE*i/_NO_OF_SAMPLES)
        
    if _SAVE_TO_FILE:
        fd = open("sawtoothWave.txt","w")
        for i in range(_NO_OF_SAMPLES):
            fd.write(str(sawtooth[i]))
            fd.write("\n ")
        fd.close
        
if _WAVEFORM == "triangular":
    # create triangular wave form
    triangular = []
    waveform=triangular
    for i in range(_NO_OF_SAMPLES//2): 
        triangular.append(_DAC_MAX_VALUE*2*i/_NO_OF_SAMPLES)
    for i in range(_NO_OF_SAMPLES//2,0,-1):
        triangular.append(_DAC_MAX_VALUE*2*i/_NO_OF_SAMPLES)
        
    if _SAVE_TO_FILE:
        fd = open("triangularWave.txt","w")
        for i in range(_NO_OF_SAMPLES):
            fd.write(str(triangular[i]))
            fd.write("\n ")
        fd.close 

# send the waveform to the DAC
if sys.platform == 'esp32':

    while True:
        try:
            for i in range(_NO_OF_SAMPLES):
                # go for max speed
                # if you want to slow down, put a sleep here
                dac.write(int(waveform[i]))
        except KeyboardInterrupt:
            break;
print("Ctrl C seen! Setting DAC to zero")
sys.exit(0)
