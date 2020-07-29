"""ST7735 demo (images)."""
from time import sleep
from ST7735 import Display
from machine import Pin, SPI
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

    display.draw_image('images/RaspberryPiWB128x128.raw', 0, 0, 128, 128)
    sleep(5)

    display.draw_image('images/MicroPython128x128.raw', 0, 0, 128, 128)
    sleep(5)

    display.draw_image('images/Tabby128x128.raw', 0, 0, 128, 128)
    sleep(5)

    display.draw_image('images/Tortie128x128.raw', 0, 0, 128, 128)
    sleep(10)

    display.cleanup()


test()
