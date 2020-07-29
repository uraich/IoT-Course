"""ST7735 demo (fonts)."""
from time import sleep
from  ST7735 import Display, color565
from machine import Pin, SPI
import fonts.ArcadePix9x11 as ArcadePix9x11
import fonts.Bally7x9 as Bally7x9
import fonts.Broadway17x15 as Broadway17x15
import fonts.EspressoDolce18x24 as EspressoDolce18x24
import fonts.FixedFont5x8 as FixedFont5x8
import fonts.Neato5x7 as Neato5x7
import fonts.Robotron7x11 as Robotron7x11
import fonts.Unispace12x24 as Unispace12x24
import fonts.Wendy7x8 as Wendy7x8

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

    display.text(0, 0, 'Arcade Pix 9x11', color565(255, 0, 0), ArcadePix9x11)
    display.text(0, 12, 'Bally 7x9', color565(0, 255, 0), Bally7x9)
    display.text(0, 23, 'Broadway', color565(0, 0, 255), Broadway17x15)
    display.text(0, 36, 'Espresso', color565(0, 255, 255), EspressoDolce18x24)
    display.text(0, 64, 'Fixed Font 5x8',  color565(255, 0, 255), FixedFont5x8)
    display.text(0, 76, 'Neato 5x7', color565(255, 255, 0), Neato5x7)
    display.text(0, 85, 'Robotron 7x11', color565(255, 255, 255), Robotron7x11)
    display.text(0, 96, 'Unispace', color565(255, 128, 0), Unispace12x24)
    display.text(0, 120, 'Wendy 7x8', color565(255, 0, 128), Wendy7x8)
    display.show()
    sleep(5)
    display.fill(0)

    display.text(0, 127, 'Arcade Pix 9x11',  color565(255, 0, 0), ArcadePix9x11 ,landscape=True)
    display.text(12, 127, 'Bally 7x9', color565(0, 255, 0), Bally7x9, landscape=True)
    display.text(23, 127, 'Broadway', color565(0, 0, 255), Broadway17x15, landscape=True)
    display.text(36, 127, 'Espresso', color565(0, 255, 255), EspressoDolce18x24, landscape=True)
    display.text(63, 127, 'Fixed Font 5x8', color565(255, 0, 255), FixedFont5x8, landscape=True)
    display.text(76, 127, 'Neato 5x7', color565(255, 255, 0), Neato5x7, landscape=True)
    display.text(85, 127, 'Robotron 7x11', color565(255, 255, 255), Robotron7x11, landscape=True)
    display.text(96, 127, 'Unispace', color565(255, 128, 0), Unispace12x24, landscape=True)
    display.text(120, 127, 'Wendy 7x8',  color565(255, 0, 128), Wendy7x8, landscape=True)
    display.show()
    sleep(5)
    display.fill(0)

    display.text(0, 0, 'Arcade Pix 9x11', color565(255, 0, 0), ArcadePix9x11,
                 background=color565(0, 255, 255))
    display.text(0, 12, 'Bally 7x9', color565(0, 255, 0), Bally7x9,
                 background=color565(0, 0, 128))
    display.text(0, 23, 'Broadway', color565(0, 0, 255), Broadway17x15,
                      background=color565(255, 255, 0))
    display.text(0, 36, 'Espresso', color565(0, 255, 255), EspressoDolce18x24,
                      background=color565(255, 0, 0))
    display.text(0, 64, 'Fixed Font 5x8', color565(255, 0, 255), FixedFont5x8,
                      background=color565(0, 128, 0))
    display.text(0, 76, 'Neato 5x7', color565(255, 255, 0), Neato5x7,
                      background=color565(0, 0, 255))
    display.text(0, 85, 'Robotron 7x11',color565(255, 255, 255), Robotron7x11,
                      background=color565(128, 128, 128))
    display.text(0, 96, 'Unispace', color565(255, 128, 0), Unispace12x24,
                      background=color565(0, 128, 255))
    display.text(0, 120, 'Wendy 7x8', color565(255, 0, 128), Wendy7x8,
                      background=color565(255, 255, 255))    
    display.show()
    sleep(5)
    display.fill(0)
        
    display.text(0, 127, 'Arcade Pix 9x11',  color565(255, 0, 0), ArcadePix9x11,
                      background=color565(0, 255, 255),landscape=True)
    display.text(12, 127, 'Bally 7x9', color565(0, 255, 0), Bally7x9 ,
                      background=color565(0, 0, 128),landscape=True)
    display.text(23, 127, 'Broadway', color565(0, 0, 255), Broadway17x15,
                      background=color565(255, 255, 0),landscape=True)
    display.text(36, 127, 'Espresso', color565(0, 255, 255), EspressoDolce18x24,
                      background=color565(255, 0, 0),landscape=True)
    display.text(64, 127, 'Fixed Font 5x8', color565(255, 0, 255), FixedFont5x8,
                      background=color565(0, 128, 0),landscape=True)
    display.text(76, 127, 'Neato 5x7',  color565(255, 255, 0), Neato5x7,
                      background=color565(0, 0, 255),landscape=True)
    display.text(85, 127, 'Robotron 7x11', color565(255, 255, 255), Robotron7x11,
                      background=color565(128, 128, 128),landscape=True)
    display.text(96, 127, 'Unispace', color565(255, 128, 0), Unispace12x24,
                      background=color565(0, 128, 255),landscape=True)
    display.text(120, 127, 'Wendy 7x8', color565(255, 0, 128), Wendy7x8,
                      background=color565(255, 255, 255),landscape=True)
    display.show()
    sleep(5)
    display.cleanup()


test()
