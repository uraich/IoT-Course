# clock program
# The program reads the current time from ntp and starts a timer with a
# frequency of 1 Hz
# The timer callback toggles the colon on the tm1637 display and updates
# hours and minutes if needed
# copyright U. Raich, 23.1.2021
# The program is part of an IoT course at the University of Cape Coast, Ghana
# released under GPL

from machine import Timer
from tm1637 import TM1637
from wifi_connect import connect,cetTime

class Clock:
    minutes = 0
    hours = 0
    colon = False
    def __init__(self):        
        #
        # connect to the WiFi network and setup the time
        #
        
        connect()

        #
        # setup the initial time
        #

        currentTime = cetTime()
        # cetTime returns (year,month,day,hours,minute,sec...)
        self.hours = currentTime[3]
        self.minutes = currentTime[4]
        time = self.hours = currentTime[3]*100+self.minutes
        # switch display on
        self.tm1637 = TM1637()
        self.tm1637.display_on()
        self.tm1637.write_dec(time,self.colon)
        # start a timer to interrupt every second
        timer = Timer(1)
        timer.init(period=1000, mode=Timer.PERIODIC, callback=self.set_clock)

    def set_clock(self,info):
        ''' timer callback updates the clock '''
        currentTime = cetTime()
        self.hours = currentTime[3]
        self.minutes = currentTime[4]
        self.colon = not self.colon
        time = self.hours = currentTime[3]*100+self.minutes
        self.tm1637.write_dec(time,self.colon)
        
clock=Clock()

