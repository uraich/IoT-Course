"""Solution to exercise 2: Text Drawing
   Copyright(c) U. Raich 2020
   This program is part of the IoT course at the 
   University of Cape Coast, Ghana
"""
from time import sleep
from ST7735 import Display, color565
from machine import Pin, SPI
import sys, time
import fonts.sysfont as sysfont
import fonts.arial10 as arial10
import fonts.courier20 as courier20
import fonts.freesans20 as freesans20
import fonts.EspressoDolce18x24 as EspressoDolce18x24


def test_text():
    display.clear()
    display.draw_text(0, 0, 'DCSIT',  arial10, Display.RED)
    display.draw_text(0, 10, 'DCSIT',  courier20, Display.GREEN)
    display.draw_text(0, 30, 'DCSIT',  EspressoDolce18x24, Display.BLUE)
    display.draw_text(0, 127, 'DCSIT',  sysfont, Display.RED,landscape=True)
    display.draw_text(10, 127, 'DCSIT',  freesans20, Display.GREEN,landscape=True)
    display.draw_text(30, 127, 'DCSIT',  EspressoDolce18x24, Display.BLUE,landscape=True)    
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

display=Display(spi,SPI_CS,SPI_DC)
test_text()
time.sleep(5)

display.cleanup()
