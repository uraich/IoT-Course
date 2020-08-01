# ntp.py Takes the time from the NTP server and sets up the RTC with the correct time
# automatically
# copyright U. Raich, 25.May 2020
# This program was written for the course on the Internet of Things at the
# University of Cape Coast,Ghana
# It is released under GPL

import network
import time,sys
from machine import *
from ntptime import settime

print("Setting the ESP32 real time clock with current date and time")
print("read from the NTP server")
print("Program written for the course on IoT at the")
print("Iniversity of Cape Coast,Ghana")
print("Copyright: U.Raich")
print("Released under the Gnu Public License")

from wifi_connect import *
from ntptime import settime

connect()
settime()
