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

def test_lines():    
    """Test code."""
    print("Test lines")
    display.clear()
    for i in range(50):
        r = random(7)
        x0 = r[0]//2
        y0 = r[1]//2
        x1 = r[2]//2
        y1 = r[3]//2
        red = r[4]
        green = r[5]
        blue = r[6]
        #rint(x0,x1,y0,y1)
        c = color565(red,green,blue)
        display.draw_line(x0,y0,x1,y1,c)
        
def test_rectangles():    
    """Test code."""
    print("Test rectangles")
    display.clear()
    for i in range(50):
        r = random(7)
        x0 = r[0]//2
        y0 = r[1]//2
        w = r[2]//2
        h = r[3]//2
        red = r[4]
        green = r[5]
        blue = r[6]
        #rint(x0,x1,y0,y1)
        c = color565(red,green,blue)
        display.draw_rectangle(x0,y0,w,h,c)
        
def test_circles():    
    """Test code."""
    print("Test circles")
    display.clear()
    for i in range(50):
        r = random(6)
        x0 = r[0]//2
        y0 = r[1]//2
        radius = r[2]//4
        red = r[3]
        green = r[4]
        blue = r[5]
        #rint(x0,x1,y0,y1)
        c = color565(red,green,blue)
        display.draw_circle(x0,y0,radius,c)
        
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
test_lines()
time.sleep(5)
display.clear()
test_rectangles()
time.sleep(5)
display.clear()
test_circles()
time.sleep(5)
display.clear()
display.cleanup()
