# ntp.py Takes the time from the NTP server and sets up the RTC with the correct time
# automatically
# copyright U. Raich, 11.May 2019
# This program was written for the workshop on IoT at the
# African Internet Summit 2019, Kampala, Uganda
# It is released under GPL

import network
import time,sys
from machine import *
from ds1307 import *
from ntptime import settime
from wifi_connect import *

CET = True
connect()

print("Setting the DS1307 read time clock with current date and time")
print("read from the NTP server")
print("Program written for the workshop on IoT at the")
print("African Internet Summit 2019")
print("Copyright: U.Raich")
print("Released under the Gnu Public License")

settime()
# print the time and date
now=time.time()
# correct for CET time zone
year = time.localtime()[0]       #get current year

if CET:
    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now=time.time()
    if now < HHMarch :               # we are before last sunday of march
        cet=time.localtime(now+3600) # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        cet=time.localtime(now+7200) # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet=time.localtime(now+3600) # CET:  UTC+1H
    tm = cet
else:
    tm = time.localtime(now)
    
print('CET: ',end='')
print(tm)

print('Date and time: ',end='');
print(tm[2],end='')
print('.',end='')
print(tm[1],end='')
print('.',end='')
print(tm[0],end='')
print('  ',end='')
# this needs modification for the workshop in Uganda!

print(tm[3],end='')     # CET
print(':',end='')
print(tm[4],end='')
print(':',end='')
print(tm[5])

# Convert to format needed by ds1307

month=tm[1]
year=tm[0]
day=tm[2]
weekday=tm[6]+1
hour=tm[3]
minute=tm[4]
sec=tm[5]
dateAndTime=(year,month,day,weekday,hour,minute,sec)

# here to set up the RTC
if sys.platform == "esp8266":
    print("Running on ESP8266")
    pinScl      =  5  #ESP8266 GPIO5 (D1
    pinSda      =  4  #ESP8266 GPIO4 (D2)
else:
    print("Running on ESP32") 
    pinScl      =  22  # SCL on esp32 
    pinSda      =  21  # SDA ON ESP32
    
# init ic2 object
i2c = I2C(scl=Pin(pinScl), sda=Pin(pinSda)) 
addrDS1307=0x68

# Scan i2c bus and check if DS1307 is connected
print('Scan i2c bus...')
devices = i2c.scan()
if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))
  ds1307IsConnected=False
  for device in devices: 
    if device == addrDS1307:
      ds1307IsConnected = True
      break
if not ds1307IsConnected:
    print("Could not find the DS1307, please connect the board!")
    sys.exit()
    
ds1307 = DS1307(i2c)
print("Setting time")
print("date and time: %s"%str(dateAndTime))
ds1307.datetime(dateAndTime)
ds1307.halt(False)
readBack=ds1307.datetime()
print(readBack)
