"""Solution to exercise 1: Random lines, rectangles and circles
   Copyright(c) U. Raich 2020
   This program is part of the IoT course at the 
   University of Cape Coast, Ghana
"""
from time import sleep
from ST7735 import Display, color565
from machine import Pin, SPI
import sys, time
from uos import urandom as random

# Fonts
import fonts.arial10 as arial10

from writer import Writer, CWriter
from fplot import CartesianGraph, Curve
from nanogui import Label, refresh
from math import cos, exp

def cart():
    print('Cartesian data test.')

    def populate_1():
        x = 0
        while x < 2.01:
            yield x, exp(-x)*cos(10*x) # x, y
            x += 0.1

    refresh(st7735, True)  # Clear any prior image
    g = CartesianGraph(wri, 20, 2, fgcolor=Display.WHITE, gridcolor=Display.LIGHT_GREEN) # Asymmetric y axis
    curve1 = Curve(g, Display.RED, populate_1(), origin = (1,0) )
    title = Label(wri, 2, 10, 'Damped Oscillator', fgcolor=Display.WHITE, bdcolor=Display.WHITE)
    refresh(st7735)
    
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
refresh(st7735)
CWriter.set_textpos(st7735, 0, 0)  # In case previous tests have altered it
wri = CWriter(st7735, arial10, Display.GREEN, Display.BLACK, verbose=False)
wri.set_clip(True, True, False)

cart()
time.sleep(25)
st7735.cleanup()
