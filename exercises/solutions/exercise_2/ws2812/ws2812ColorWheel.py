# ws1812ColorWheel: Shows all the colors of the rainbow 
#
# U. Raich, 10.Jun 2021
# This program was written for the course on IoT at the University of Cape Coast,Ghana

import machine, neopixel, time, sys
from micropython import const

DATA_PIN   = const(26)
NO_OF_LEDS = const(7)
MAX_INTENS = const(0x1f)

neoPixel = neopixel.NeoPixel(machine.Pin(DATA_PIN), NO_OF_LEDS)

def setNeoPixels(colors):
    for i in range(NO_OF_LEDS):
        neoPixel[i] = colors
    neoPixel.write()

while True:
    try:
        for angle in range(360):
            if angle == 0:
                print("0..60 degrees")
            if angle == 60:
                print("60..120 degrees")
            if angle == 120:
                print("120..180 degrees")
            if angle == 180:
                print("180..2400 degrees")
            if angle == 240:
                print("240..300 degrees")
            if angle == 300:
                print("300..360 degrees")
        
        
            if angle < 60:
                colors = [MAX_INTENS,int(angle*MAX_INTENS/60),0]
            elif angle >= 60 and angle < 120:
                colors = [int(MAX_INTENS - MAX_INTENS*(angle-60)/60),MAX_INTENS,0]
            elif angle >= 120 and angle < 180:
                colors = [0,MAX_INTENS,int((angle-120)*MAX_INTENS/60)]
            elif angle >= 180 and angle < 240:
                colors = [0,int(MAX_INTENS-(angle-180)*MAX_INTENS/60),MAX_INTENS]
            elif angle >= 240 and angle < 300:
                colors = [int(MAX_INTENS*(angle-240)/60),0,MAX_INTENS]
            else:
                colors = [MAX_INTENS,0,int(MAX_INTENS - MAX_INTENS*(angle-300)/60)]
            print(colors)

            setNeoPixels(colors)
            time.sleep_ms(30)
    except KeyboardInterrupt:
        setNeoPixels((0,0,0))
        break
