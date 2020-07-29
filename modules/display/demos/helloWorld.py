"""SSD1351 demo (fonts)."""
from time import sleep
from  ST7735 import Display, color565
from machine import Pin, SPI
import fonts.sysfont as sysfont
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


def test():
    """Test code."""
    display=Display(spi,SPI_CS,SPI_DC)
    display.clear()

    display.draw_text(0, 0, 'Hello World!', sysfont, color565(255, 0, 0))
    display.text(20,20,'Good bye World!',color565(255, 0, 0))
    display.draw_text(10, 100, 'Hello World!', sysfont, color565(255, 0, 0),landscape=True)
    sleep(9)
    display.cleanup()


test()
