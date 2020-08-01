# initialize the WiFi network
# read the current time from NTP and setup the ESP32 Real Time Clock
# Copyright (c) U. Raich, May 2020
#
import network,sys,time
from ntptime import settime

def connect():
    encoding          ='utf-8'
    ssid              = "your_SSID"
    password          = "your password"
    
    station = network.WLAN(network.STA_IF)
    if station.isconnected() == True:
        print("Already connected")
        return
    
    if station.active():
        print("Station is already active")
    else:
        print ("Activating station")
        if not station.active(True):
            print("Cannot activate station! giving up ...")
            sys.exit()
            
    accessPoints = station.scan()
    print(len(accessPoints), "access points found")
    
    if ssid == "your_SSID":
        print("Please modify the code and add your SSID and password")
        sys.exit()
        
    station.connect(ssid, password)
 
    while station.isconnected() == False:
      pass
 
    print("Connection successful")
    
    # setup system time
    settime()
    
    print(station.ifconfig())


def getIPAddress():
    station = network.WLAN(network.STA_IF)
    return station.ifconfig()[0]
    
def gmtTime():
    return time.localtime(time.time())

def cetTime():
    settime()
    # print the time and date
    now=time.time()
    
    # correct for CET time zone
    year = time.localtime()[0]       #get current year

    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now=time.time()
    if now < HHMarch :               # we are before last sunday of march
        cet=time.localtime(now+3600) # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        cet=time.localtime(now+7200) # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet=time.localtime(now+3600) # CET:  UTC+1H
    return cet

