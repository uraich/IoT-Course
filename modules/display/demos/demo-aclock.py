# aclock.py Test/demo program for Adafruit ssd1351-based OLED displays
# Adafruit 1.5" 128*128 OLED display: https://www.adafruit.com/product/1431
# Adafruit 1.27" 128*96 display https://www.adafruit.com/product/1673

# The MIT License (MIT)

# Copyright (c) 2018 Peter Hinch

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# height = 96  # 1.27 inch 96*128 (rows*cols) display
height = 128 # 1.5 inch 128*128 display

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

from machine import Pin,SPI
import gc
from ST7735 import Display, color565
import sys
from wifi_connect import *

# Initialise hardware
if sys.platform == 'esp8266':
    print('1.4 inch TFT screen test on ESP8266')
    SPI_CS = 16
    SPI_DC = 15
    spi = SPI(1)
    
elif sys.platform == 'esp32':
    print('1.4 inch TFT screen test on ESP32')
    sck = Pin(18)
    miso= Pin(19)
    mosi= Pin(23)
    SPI_CS = 26
    SPI_DC = 5
    spi = SPI(2, baudrate=32000000, sck=sck, mosi=mosi, miso=miso)
    
st7735=Display(spi,SPI_CS,SPI_DC)

gc.collect()  # Precaution before instantiating framebuf

from nanogui import Dial, Pointer, refresh, Label

# Now import other modules
import cmath
import utime
from writer import CWriter
import fonts.arial10 as arial10

GREEN = color565(0, 255, 0)
RED = color565(255, 0, 0)
BLUE = color565(0, 0, 255)
YELLOW = color565(255, 255, 0)
BLACK = 0

def aclock():
    uv = lambda phi : cmath.rect(1, phi)  # Return a unit vector of phase phi
    pi = cmath.pi
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')
    months = ('Jan', 'Feb', 'March', 'April', 'May', 'June', 'July',
              'Aug', 'Sept', 'Oct', 'Nov', 'Dec')

    CWriter.set_textpos(st7735, 0, 0)  # In case previous tests have altered it
    wri = CWriter(st7735, arial10, GREEN, BLACK, verbose=False)
    wri.set_clip(True, True, False)
    
    # Instantiate displayable objects
    refresh(st7735, True)  # Clear any prior image
    dial = Dial(wri, 2, 2, height = 75, ticks = 12, bdcolor=None, label=120, pip=False)  # Border in fg color
    lbltim = Label(wri, 5, 85, 35)
    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart =  0 + 0.7j  # Pointer lengths and position at top
    mstart = 0 + 0.92j
    sstart = 0 + 0.92j 
    while True:
        t = cetTime()
        hrs.value(hstart * uv(-t[3]*pi/6 - t[4]*pi/360), YELLOW)
        mins.value(mstart * uv(-t[4] * pi/30), YELLOW)
        secs.value(sstart * uv(-t[5] * pi/30), RED)
        lbltim.value('{:02d}.{:02d}.{:02d}'.format(t[3], t[4], t[5]))
        dial.text('{} {} {} {}'.format(days[t[6]], t[2], months[t[1] - 1], t[0]))
        refresh(st7735)
        utime.sleep(1)

print ("Connecting to the network")
connect()
print("Connected with IP ",getIPAddress())
aclock()
