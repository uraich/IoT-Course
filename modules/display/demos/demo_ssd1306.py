# the ssd1306 graphics test ported to the ST7735
# copyright (c) U. Raich 20.7.2020
import sys
import time 
from machine import Pin,SPI
from math import sin,pi
from ST7735 import Display
import fonts.sysfont as sysfont

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

from time import sleep
import fonts.sysfont as sysfont

print("Testing the st7735 OLED display")
print("Program written for the course on IoT at the")
print("University of Cape Coast")
print("Copyright: U.Raich")
print("Released under the Gnu Public License")

hSize       = 128  # Hauteur ecran en pixels | display heigh in pixels
wSize       = 128  # Largeur ecran en pixels | display width in pixels

if sys.platform == 'esp8266':
    oled = ST7735(spi,SPI_CS,SPI_DC)
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

def testDrawLine(color):
    for i in range(0,wSize,4):
        oled.draw_line(0,0,i,hSize-1,color)
        time.sleep(0.1)
    for i in range(0,hSize,4):
        oled.draw_line(0,0,wSize-1,hSize-i-4,color)
        time.sleep(0.1)
        
def testDrawRect(color):
    for i in range (0,hSize//2,2):
        oled.draw_rectangle(i,i,wSize-2*i,hSize-2*i,color)
        time.sleep(0.1)

def testFillRect(framecolor,color):
    for i in range(3,hSize//2,3):
        oled.draw_filledRectangle(i,i,i*2,i*2,color)
        oled.draw_rectangle(i,i,i*2,i*2,framecolor)
        time.sleep(0.1)
        
def testDrawCircles():
    oled.draw_circle(50,50,50,oled.GREEN)
    oled.draw_circle(65,35,30,oled.BLUE)
    oled.draw_circle(25,15,15,oled.RED)
    oled.draw_circle(5,15,5,oled.YELLOW)
    
def drawSin(color):
    oled.draw_hline(0,hSize//2,wSize-1,color)
    oled.draw_vline(0,0,hSize-1,color)
    for i in range(0,wSize):
        oled.draw_pixel(i,round(-sin(2*pi*i/wSize)*hSize//2)+hSize//2,color)
    oled.draw_text(wSize//4,hSize//5,"sin(x)",sysfont,color)
                
spi = SPI(2, baudrate=32000000, sck=sck, mosi=mosi, miso=miso)

oled = Display(spi,SPI_CS,SPI_DC)
oled.clear()
print("Draw line test")
oled.clear()
testDrawLine(oled.YELLOW)
sleep(1)
oled.clear()
print("Draw rectangle test")
testDrawRect(oled.BLUE)
time.sleep(1)
oled.clear()
print("Draw filled rectangle test")
testFillRect(oled.DARKGREEN,oled.GREEN)
time.sleep(1)
oled.clear()
print("Draw circle test")
testDrawCircles()
time.sleep(1)
oled.clear()
print("Draw sin function")
drawSin(oled.WHITE)
time.sleep(1)

