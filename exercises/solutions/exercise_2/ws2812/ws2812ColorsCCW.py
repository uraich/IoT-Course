# ws2812Colors.py: controls the ws2812b rgb LED chain
# The program switches the leds on consecutively, a new one every second. Once all leds are on they are all switched
# off again and the cycle repeats with a new color. The basic colors red, green, blue are cycled.
# U. Raich, 19.May 2020
# This program was written for the course on IoT at the University of Cape Coast,Ghana


import machine, neopixel, time, sys

n=7        # number of LEDs

print("Testing the ws2812 rgb LED")
print("The program switches leds on consecutively with changing colors")
print("Program written for the course on IoT at the")
print("University of Cape Coast,Ghana")
print("Copyright: U.Raich")
print("Released under the Gnu Public License")

def clearChain():
    for i in range(n):
        neoPixel[i] = (0, 0, 0)
    neoPixel.write()

        
if sys.platform == "esp8266":
    print("Running on ESP8266")
    pin = 16   # connected to GPIO 4 on esp8266
else:
    print("Running on ESP32") 
    pin = 26   # connected to GPIO 21 on esp32
    
neoPixel = neopixel.NeoPixel(machine.Pin(pin), n)
colors = { 0: [0x3f,0,0],
           1: [0,0x3f,0],
           2: [0,0,0x3f]}

for c in range(3):
    clearChain()
    if c != 0:
        time.sleep(1)
    for i in range(2):
        neoPixel[i] = (colors[c][0],colors[c][1],colors[c][2])
        neoPixel.write()
        time.sleep(1)
    for i in range(n-2):
        neoPixel[n-i-1] = (colors[c][0],colors[c][1],colors[c][2])
        neoPixel.write()
        time.sleep(1)

clearChain()

