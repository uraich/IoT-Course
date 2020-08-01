# ds1307Test tests the DS1307 driver
# U. Raich 25.3.2019
#
from machine import *
from ds1307 import *
import sys

print("Testing the DS1307 real time clock")
print("Program written for the workshop on IoT at the")
print("African Internet Summit 2019")
print("Copyright: U.Raich")
print("Released under the Gnu Public License")
if sys.platform == "esp8266":
    print("Running on ESP8266")
    pinScl      =  5  #ESP8266 GPIO5 (D1
    pinSda      =  4  #ESP8266 GPIO4 (D2)
else:
    print("Running on ESP32") 
    pinScl      =  22  # SCL on esp32 
    pinSda      =  21  # SDA ON ESP32

addrDS1307=0x68
# dateAndTime: yy mm dd ww hh mm ss 
def monthString(m):
  return{
    1:      'January', 
    2:      'February', 
    3:      'March', 
    4:      'April', 
    5:      'May', 
    6:      'June', 
    7:      'July', 
    8:      'August', 
    9:      'September',
    10:     'October',  
    11:     'November', 
    12:     'December', 
    } [m]

def weekdayString(w):
    return {
    1:       'Monday',
    2:       'Tuesday',
    3:       'Wednesday',
    4:       'Thursday',
    5:       'Friday',
    6:       'Saturday',
    7:       'Sunday',
    }[w]
    
YEAR=0
MONTH=1
DAY=2
WEEKDAY=3
HOUR=4
MIN=5
SEC=6

# init ic2 object
i2c = I2C(scl=Pin(pinScl), sda=Pin(pinSda)) #ESP8266 5/4

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
    
print("Creating DS1307 object")
ds1307 = DS1307(i2c)

dateAndTime=ds1307.datetime()
year=dateAndTime[YEAR]
day=dateAndTime[DAY]
month=monthString(dateAndTime[MONTH])
weekday=weekdayString(dateAndTime[WEEKDAY])
hour=dateAndTime[HOUR]
mins=dateAndTime[MIN]
secs=dateAndTime[SEC]
print("We are %s %d %s %d time: %d:%d:%d"%(weekday,day,month,year,hour,mins,secs))
