from machine import Pin,SPI
import gc,sys
from ST7735 import Display,color565
from sht3x import SHT3X,SHT3XError
from nanogui import Label, Meter, refresh

# Fonts
import fonts.arial10 as arial10
from writer import Writer, CWriter
import utime
import uos

# create a SHT3X object
try:
    sht30 = SHT3X()
except SHT3XError as exception:
    if exception.error_code == SHT3XError.BUS_ERROR:
        print("SHT30 module not found on the I2C bus, please connect it")
        sys.exit(-1)
    else:
         raise exception
        
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

CWriter.set_textpos(st7735, 0, 0)  # In case previous tests have altered it
wri = CWriter(st7735, arial10, Display.GREEN, Display.BLACK, verbose=False)
wri.set_clip(True, True, False)

def meter():
    print('meter')

    refresh(st7735, True)  # Clear any prior image
    title = Label(wri, 2, 10, 'SHT30 measurements', fgcolor=Display.WHITE, bdcolor=Display.WHITE)
    tempLabel = Label(wri, 110, 2, '32.4 deg C', fgcolor=Display.WHITE, bdcolor=Display.BLACK)
    humiLabel = Label(wri, 110, 80, '42 %', fgcolor=Display.WHITE, bdcolor=Display.BLACK)
    mtemp = Meter(wri, 25, 2, height = 70, divisions = 5, ptcolor=Display.YELLOW,
              label='temperature', style=Meter.BAR, legends=('0','10', '20', '30', '40','50'))

    mhumi = Meter(wri, 25, 80, height = 70, divisions = 5, ptcolor=Display.YELLOW,
              label='humidity', style=Meter.BAR, legends=('0', '20', '40', '60', '80','100'))

    steps = 11

    for i in range(steps):
        tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
        #print("Temperature: ",tempC,"°C, Humidity: ",humi,"%")
        humiText = "{0:.1f} %".format(humi)
        tempText = "{0:.1f} deg C".format(tempC)
        t = tempC/50.0
        h = humi/100.0
        mtemp.value(t)
        mhumi.value(h)
        tempLabel.value(tempText)
        humiLabel.value(humiText)

        #print(humiText)
        refresh(st7735)
        utime.sleep(1)
    refresh(st7735)

meter()
