"""SSD1351 demo (shapes)."""
from time import sleep
from ST7735 import Display, color565
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
    print('display started')

    display.clear(color565(64, 0, 255))
    sleep(1)

    display.clear()

    display.draw_hline(10, 127, 63, color565(255, 0, 255))
    sleep(1)

    display.draw_vline(10, 0, 127, color565(0, 255, 255))
    sleep(1)

    display.draw_filledRectangle(23, 50, 30, 75, color565(255, 255, 255))
    sleep(1)

    display.draw_hline(0, 0, 127, color565(255, 0, 0))
    sleep(1)

    display.draw_line(127, 0, 64, 127, color565(255, 255, 0))
    sleep(2)

    display.clear()

    coords = [[0, 63], [78, 80], [122, 92], [50, 50], [78, 15], [0, 63]]
    display.draw_lines(coords, color565(0, 255, 255))
    sleep(1)

    display.clear()
    display.draw_filledPolygon(7, 63, 63, 50, color565(0, 255, 0))
    sleep(1)

    display.draw_filledRectangle(0, 0, 15, 127, color565(255, 0, 0))
    sleep(1)

    display.clear()

    display.draw_filledRectangle(0, 0, 63, 63, color565(128, 128, 255))
    sleep(1)

    display.draw_rectangle(0, 64, 63, 63, color565(255, 0, 255))
    sleep(1)

    display.draw_filledRectangle(64, 0, 63, 63, color565(128, 0, 255))
    sleep(1)

    display.draw_polygon(3, 96, 96, 30, color565(0, 64, 255),
                         rotate=15)
    sleep(3)

    display.clear()

    display.draw_filledCircle(32, 32, 30, color565(0, 255, 0))
    sleep(1)

    display.draw_circle(32, 96, 30, color565(0, 0, 255))
    sleep(1)

    display.draw_filledEllipse(96, 32, 30, 16, color565(255, 0, 0))
    sleep(1)

    display.draw_ellipse(96, 96, 16, 30, color565(255, 255, 0))

    sleep(5)
    display.cleanup()


test()
