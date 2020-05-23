# sht3xTest.py is a program to exercise the sht3x module, a driver for
# the SHT30 temperature and humidity sensor
# Copyright (c) U. Raich, May 2020
# The program was written for the course on the Internet of Things
# at the University of Cape Coast, Ghana
# It is released under GPL

# import the SHT3X class
from sht3x import SHT3X,SHT3XError
import sys
# This is a simple callback function printing temperature and humidity values
# read in continuous measurement
def printContinuousValues(value):
    print("Temperature: ",value[0], "°C, Humidity: ",value[1],"%")
    
# create a SHT3X object
try:
    sht30 = SHT3X()
except SHT3XError as exception:
    if exception.error_code == SHT3XError.BUS_ERROR:
        print("SHT30 module not found on the I2C bus, please connect it")
        sys.exit(-1)
    else:
         raise exception
        
# read out the serial number
print("Serial number: ",hex(sht30.serialNumber()))

# demonstrate a single shot measurement with clock-stretching
print("Measure with clock stretching, the delay between writing the cmd and reading back the result")
print("is calculated from the repeatabilty parameter (see data sheet)")
tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
print("Temperature: ",tempC,"°C, Humidity: ",humi,"%")

# demonstrate a single shot measurement without clock-stretching
print("Measure without clock stretching")
print("After sending the command the SHT30 is polled for the result every 1ms")
print("Generates a timeout exception if the SHT30 does not respond in time")
tempC, humi = sht30.getTempAndHumi(clockStretching=SHT3X.NO_CLOCK_STRETCH,repeatability=SHT3X.REP_S_HIGH)
print("Temperature: ",tempC,"°C, Humidity: ",humi,"%")

print("Read and print the alert settings: High limit to set the alert")
print("The data sheet says that this should be 60°C and 80%")
temp,humi = sht30.readAlert()
tempLimit=60
humiLimit=80
sht30.writeAlert(tempLimit,humiLimit)
print("Temperature limit high: ",temp, "°C Humidity limit high: ",humi,"%")

print("Set accelerated response time")
sht30.setART()
print("Print the current status register contents")
sht30.printStatus()
print("Clear the status register, switch on the heater and print the values again")
sht30.clearStatus()
print("Switch on the heater")
sht30.enableHeater()
sht30.printStatus()

print("Start periodic measurement")
print("We pass the function printContinuousValues as callback routine, printing the temperature and humidity values")
print("read out in each measurement cycle")
count = 10
measurementsPerSecond = 0.5
print("Period measurement will take ",1/measurementsPerSecond * count,"s")
result=sht30.measPeriodic(mps=measurementsPerSecond, noOfMeas=count,callback=printContinuousValues)
sht30.enableHeater()
sht30.printStatus()
