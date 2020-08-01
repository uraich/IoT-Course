# sht3xReadout.py
# -- mounts the SD card
# -- create a data directory on the SD card if it does not already exist
# -- reads out temperature and humidity values from the SHT30
# -- gets the time stamp of the measurement
# -- write time stamp and SHT30 data to the sht30Data.txt file
# 
# Copyright (c) U. Raich, May 2020
# The program was written for the course on the Internet of Things
# at the University of Cape Coast, Ghana
# It is released under GPL

# import the SHT3X class
from sht3x import SHT3X,SHT3XError
import sys, os, sdcard, machine
import errno
from wifi_connect import *
from ntptime import settime
import network

# connect to the Internet
connect()
station = network.WLAN(network.STA_IF)
print("ESP32 IP address: ", station.ifconfig())
# get the current time
settime()

if sys.platform == 'esp8266':
    print('SD-card test on ESP8266')
    SPI_CS = 15
    spi = machine.SPI(1)

elif sys.platform == 'esp32':
    print('SD-card test on ESP32')
    sck = machine.Pin(18)
    miso= machine.Pin(19)
    mosi= machine.Pin(23)
    SPI_CS = 5
    spi = machine.SPI(2, baudrate=32000000, sck=sck, mosi=mosi, miso=miso)

sdcardAvail=True
spi.init()  # Ensure right baudrate   
try:
    sd = sdcard.SDCard(spi, machine.Pin(SPI_CS)) # ESP8266 version
except:
    sdcardAvail = False
    
if sdcardAvail:
    print("sdcard created")
else:
    print("No sdcard found")
    sys.exit(-1)

vfs = os.VfsFat(sd)

try:
    os.mount(vfs, '/sd')
except OSError as e:
    if len(e.args) > 0 and e.args[0] == errno.EPERM:
        print('Already mounted, skipping')
        pass
    else:
        print('problem mounting the sd card')
        sys.exit(-1)

print("SD card successfully mounted")

# check it /sd/data exists and create it if not

try:
    os.stat("/sd/data")
except OSError as e:
    if len(e.args) > 0 and e.args[0] == errno.ENOENT:
        print("/sd/data does not exist, creating it")
        os.mkdir("/sd/data")

try:
    os.remove("/sd/data/sht30Data.txt")
except OSError as e:
    if len(e.args) > 0 and e.args[0] == errno.ENOENT:
        pass
        
# create a SHT3X object
try:
    sht30 = SHT3X()
except SHT3XError as exception:
    if exception.error_code == SHT3XError.BUS_ERROR:
        print("SHT30 module not found on the I2C bus, please connect it")
        sys.exit(-1)
    else:
         raise exception

print("Found SHT30, starting readout")

for i in range(10):
    # read temperature and humidity
    tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
    now = time.time()
    f = open("/sd/data/sht30Data.txt","a")
    txt = "Time stamp: %d, Temperature: %f, Humidity: %f%%\n"%(now,tempC,humi)
    print(txt,end="")
    
    f.write(txt)
    f.close()
    time.sleep(5)
    
