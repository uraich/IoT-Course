# writer_demo.py Demo pogram for rendering arbitrary fonts to an SSD1306 OLED display.
# Illustrates a minimal example. Requires ssd1306_setup.py which contains
# wiring details.

# The MIT License (MIT)
#
# Copyright (c) 2018 Peter Hinch
#
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


# https://learn.adafruit.com/monochrome-oled-breakouts/wiring-128x32-spi-oled-display
# https://www.proto-pic.co.uk/monochrome-128x32-oled-graphic-display.html

# V0.3 13th Aug 2018

from machine import Pin,SPI
from ST7735 import Display
from writer import CWriter
import sys

# Font
import fonts.freesans20 as freesans20

def test():
    st7735.clear()
    rhs = st7735.size()[0] -1
    print("rhs: ",rhs)
    st7735.line(rhs - 20, 0, rhs, 20, Display.WHITE)
    square_side = 10
    st7735.fill_rect(rhs - square_side, 0, square_side, square_side, Display.BLUE)

    wri = CWriter(st7735, freesans20)
    wri.setcolor(Display.GREEN,Display.BLACK)
    wri.set_textpos(st7735, 0, 0)  # verbose = False to suppress console output
    wri.printstring('Sunday\n')
    wri.printstring('12 Aug 2018\n')
    wri.printstring('10.30am')
    st7735.show()

print('Test assumes a 128*128 (w*h) st7735')
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
test()
