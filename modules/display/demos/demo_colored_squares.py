"""ST7735 demo (colored squares)."""
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

    
RED = const(0x00f8)  # (255, 0, 0)
GREEN = const(0xe007)  # (0, 255, 0)
BLUE = const(0x1f00)  # (0, 0, 255)
YELLOW = const(0xe0ff)  # (255, 255, 0)
FUCHSIA = const(0x1ff8)  # (255, 0, 255)
AQUA = const(0xff07)  # (0, 255, 255)
MAROON = const(0x0080)  # (128, 0, 0)
DARKGREEN = const(0x0004)  # (0, 128, 0)
NAVY = const(0x1000)  # (0, 0, 128)
TEAL = const(0x1004)  # (0, 128, 128)
PURPLE = const(0x1080)  # (128, 0, 128)
OLIVE = const(0x0084)  # (128, 128, 0)
ORANGE = const(0x00fc)  # (255, 128, 0)
DEEP_PINK = const(0x10f8)  # (255, 0, 128)
CHARTREUSE = const(0xe087)  # (128, 255, 0)
SPRING_GREEN = const(0xf007)  # (0, 255, 128)
INDIGO = const(0x1f80)  # (128, 0, 255)
DODGER_BLUE = const(0x1f04)  # (0, 128, 255)
CYAN = const(0xff87)  # (128, 255, 255)
PINK = const(0x1ffc)  # (255, 128, 255)
LIGHT_YELLOW = const(0xf0ff)  # (255, 255, 128)
LIGHT_CORAL = const(0x10fc)  # (255, 128, 128)
LIGHT_GREEN = const(0xf087)  # (128, 255, 128)
LIGHT_SLATE_BLUE = const(0x1f84)  # (128, 128, 255)
WHITE = const(0xffff)  # (255, 255, 255)

colors= [RED,GREEN,BLUE,YELLOW,FUCHSIA,AQUA,MAROON,DARKGREEN,NAVY,
         TEAL,PURPLE,OLIVE,ORANGE,DEEP_PINK,CHARTREUSE,SPRING_GREEN,
         INDIGO,DODGER_BLUE,CYAN,PINK,LIGHT_YELLOW,LIGHT_CORAL,LIGHT_GREEN,
         LIGHT_SLATE_BLUE,WHITE]

def test():    
    """Test code."""

    display=Display(spi,SPI_CS,SPI_DC)
    colors.sort()
    c = 0
    for x in range(1, 126, 25):
        for y in range(1, 126, 25):
            display.draw_filledRectangle(x, y, 25, 25, colors[c])
            c += 1
    sleep(9)
    display.cleanup()



test()
