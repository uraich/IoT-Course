# sync.py snchronize the ESP32 real time clock (RTC) and the
# ds1307 RTC
# copyright U. Raich, 11.May 2019
# This program was written for the workshop on IoT at the
# African Internet Summit 2019, Kampala, Uganda
# It is released under GPL

import network
import time,sys
from machine import *
from ds1307 import *
from wifi_connect import *

def dayOfWeek(year,month,day):

    centuryCodeTable={
        1700: 4,
        1800: 2,
        1900: 0,
        2000: 6,
        2100: 4,
        2200: 2,
        2300: 0,
    }
    
    monthCodeTable = {
        1: 0,
        2: 3,
        3: 3,
        4: 6,
        5: 1,
        6: 4,
        7: 6,
        8: 2,
        9: 5,
        10: 0,
        11: 3,
        12: 5
    }
    
    y=year%100 # take only
    yearCode = y//4 + y
    yearCode %= 7

    print("Year code: ",yearCode)

    century = year//100 * 100
    
    centuryCode =  centuryCodeTable[century]
    print("Century Code: ",centuryCode)
    if year % 400 == 0:
        leapYearCode = 1
    elif year % 100 == 0:
        leapyearCode = 0
    elif year % 4 == 0:
        leapYearCode = 1
    else:
        leapYearCode = 0
        
    monthCode = monthCodeTable[month]
    dayCode = yearCode + monthCode + centuryCode +day
    print("leapYearCode: ",leapYearCode)
    if month == 1 or month == 2:
        dayCode -= leapYearCode
        
    return dayCode % 7

def dayOfWeekString(dayCode):
    weekDayTable= {
        0: "Sun",
        1: "Mon",
        2: "Tue",
        3: "Wed",
        4: "Thu",
        5: "Fri",
        6: "Sat",
    }
    return weekDayTable[dayCode]

def initDS1307():
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
        return None
    else:
        print('i2c devices found:',len(devices))
        
    for device in devices: 
        if device == addrDS1307:
            ds1307IsConnected = True
            break
        if not ds1307IsConnected:
            print("Could not find the DS1307, please connect the board!")
            return None
                
    return DS1307(i2c)
        
def eps32RTC2ds1307RTC():
    ds1307 = initDS1307()
    if ds1307 == None:
        print("No DS1307 found")
        return
    
    now = time.time()
    # Convert to format needed by ds1307
    tm=time.localtime(now)

    month=tm[1]
    year=tm[0]
    day=tm[2]
    weekday = dayOfWeek(year,month,day)
    print("weekday: ",dayOfWeekString(weekday))
#    weekday=tm[6]+1
    hour=tm[3]
    minute=tm[4]
    sec=tm[5]
    dateAndTime=(year,month,day,weekday+1,hour,minute,sec)
    print("Setting time")
    print("date and time: %s"%str(dateAndTime))
    ds1307.datetime(dateAndTime)
    ds1307.halt(False)
    readBack=ds1307.datetime()
    print(readBack)

def ds1307RTC2esp32RTC():
    ds1307 = initDS1307()
    if ds1307 == None:
        print("No DS1307 found")
        return
    ds1307Time = ds1307.datetime()
    print("Time from ds1307: ",ds1307Time)
    esp32RTC = RTC()
    esp32RTC.datetime(ds1307Time)
    print("Esp32 date and time after syncing: ",esp32RTC.datetime())
    
eps32RTC2ds1307RTC()
ds1307RTC2esp32RTC()