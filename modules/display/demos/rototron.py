"""ST7735 demo (bouncing sprite)."""
from ST7735 import Display
from machine import Pin, SPI
from utime import sleep_us, ticks_us, ticks_diff
import sys

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
display.clear()
buf=display.load_sprite('images/Rototron128x26.raw',128,26)
display.draw_sprite(buf,0,50,128,26)
