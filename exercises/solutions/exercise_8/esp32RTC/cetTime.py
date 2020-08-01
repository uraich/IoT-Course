# cetTime: reads the current time from the ESP32 RTC
# converts it to UTC time to CET time and prints it
# U. Raich May 2020
#

import time
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
tm = cet
    
print('CET: ',end='')
print(tm)
