#!/usr/bin/python3
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
    
if __name__ == "__main__":
    print("Day in the week 1897 3 14: ",dayOfWeek(1897,3,14))
    print("Day in the week 1969 7 20: ",dayOfWeek(1969,7,20))
    print("Day in the week 2000 1 1: ",dayOfWeek(2000,1,1))
    print("Day in the week 2020 5 6: ",dayOfWeek(2020,5,6))

for i in range(7):
    print(i, " corresponds to ",dayOfWeekString(i))
    
    
    
