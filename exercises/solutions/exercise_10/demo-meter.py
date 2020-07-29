from machine import Pin,SPI
import gc,sys
from ST7735 import Display,color565

from nanogui import Label, Meter, LED, refresh

# Fonts
import fonts.arial10 as arial10
from writer import Writer, CWriter
import utime
import uos

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

st7735 = Display(spi,SPI_CS,SPI_DC)
refresh(st7735)

GREEN = color565(0, 255, 0)
RED = color565(255, 0, 0)
BLUE = color565(0, 0, 255)
YELLOW = color565(255, 255, 0)
BLACK = 0

CWriter.set_textpos(st7735, 0, 0)  # In case previous tests have altered it
wri = CWriter(st7735, arial10, GREEN, BLACK, verbose=False)
wri.set_clip(True, True, False)

def meter():
    print('meter')
    refresh(st7735, True)  # Clear any prior image
    mtemp = Meter(wri, 5, 2, height = 100, divisions = 7, ptcolor=YELLOW,
              label='temperature', style=Meter.BAR, legends=('0', '5', '10', '20', '30', '40','50'))

    htemp = Meter(wri, 5, 80, height = 100, divisions = 6, ptcolor=YELLOW,
              label='humidity', style=Meter.BAR, legends=('0', '20', '40', '60', '80','100'))

    steps = 10
    for _ in range(steps):
        v = int.from_bytes(uos.urandom(3),'little')/16777216
        mtemp.value(v)
        htemp.value(v)
        refresh(st7735)
        utime.sleep(1)
    refresh(st7735)

meter()
