#!/usr/bin/python3
#
# functions to set up the EPS32 internal real time clock
#
# Copyright (c) U. Raich, May 2020
#
import time
from ntptime import settime
from machine import RTC

#
# algorithm from
# https://artofmemory.com/blog/how-to-calculate-the-day-of-the-week-4203.html
#

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
        12: 5,
    }
    
    y=year%100 # take only
    yearCode = y//4 + y
    yearCode %= 7

#    print("Year code: ",yearCode)

    century = year//100 * 100
    
    centuryCode =  centuryCodeTable[century]
#    print("Century Code: ",centuryCode)
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
#    print("leapYearCode: ",leapYearCode)
    if month == 1 or month == 2:
        dayCode -= leapYearCode
        
    return (dayCode % 7)

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

def parse(currentTimeInput):
    daysInMonth= {
        1: 31,
        2: 29,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
        }
        
    global currentTime
    currentTimeStrings = currentTimeInput.split()
    if len(currentTimeStrings) != 6:
        print("Input ",currentTimeInput," is not in the format: yyyy mm dd hh mm ss")
        return False
    # check the year
    try:
        year = int(currentTimeStrings[0])
    except ValueError:
        print(currentTimeStrings[0]," is not a valid year")
        return False
    if year < 2020 or year > 2050:
        print("Year is out of reach: ",year)
        return False
    
    try:
         month = int(currentTimeStrings[1])
    except ValueError:
        print(currentTimeStrings[1]," is not a valid month")
        return False
    if month < 1 or month > 12:
        print("Invalid month: ",month)
        return False
    
    try:
         day = int(currentTimeStrings[2])
    except ValueError:
        print(currentTimeStrings[2]," is not a valid month")
        return False
    if day < 1 or day > daysInMonth[month]:
        print("Invalid day: ",day)
        return False
    
    # 29 days in February only during a leap year
    
    if month == 2 and day == 29 and not year%4:
        print("Invalid day: ",day)
        return False

    try:
         hour = int(currentTimeStrings[3])
    except ValueError:
        print(currentTimeStrings[3]," is not a valid hour")
        return False
    if hour < 0 or hour > 23:
        print("Invalid day: ",hour)
        return False

    try:
         minutes = int(currentTimeStrings[4])
    except ValueError:
        print(currentTimeStrings[4]," is not a value number for minutes")
        return False
    if minutes < 0 or minutes > 59:
        print("Invalid minutes: ",minutes)
        return False

    try:
         secs = int(currentTimeStrings[5])
    except ValueError:
        print(currentTimeStrings[5]," is not a valid number for seconds")
        return False
    if secs < 0 or secs > 59:
        print("Invalid seconds: ",secs)
        return False
    dayInWeek=dayOfWeek(year,month,day)
    currentTime=(year,month,day,dayInWeek,hour,minutes,secs,0)
    
    return True
    
def rtcSetUserTime():
    global currentTime

    while True:
        print("Please enter the time in the following format: yyyy mm dd hh mm ss: ",end="")
        currentTimeInput = input()
        if parse(currentTimeInput):
            rtc=RTC()
            print("Setting time: ",currentTime)
            rtc.datetime(currentTime)
            print("Input ok")
            break;
            
def rtcSetTime(year,month,day,hours,minutes,secs):
    rtc=RTC()
    currentTime = (year,month,day,0,hours,minutes,secs,0)
    rtc.datetime(currentTime)
        
def rtcGetTime():
    rtc=RTC()
    currentTime = rtc.datetime()
    return (currentTime[0],currentTime[1],currentTime[2],currentTime[4],currentTime[5],currentTime[6])
