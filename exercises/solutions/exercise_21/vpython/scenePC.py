#!/usr/bin/python
## This program reads data over the serial port
## from that arduino. You have to read an entire line of data
## and then you have to parse it into different number values
## Then those R, G, B numbers are used to make the color of
## a visual object in python change.

import warnings
warnings.simplefilter("ignore",FutureWarning) # ignore FutureWarnings

from visual import * #import vPython library

# import the ultra-sonic ranger library
import time
##import pigpio
##import sonar_trigger_echo
##import TCS3200

def wait_for_return(str):
  if sys.hexversion < 0x03000000:
     raw_input(str)
  else:
     input(str)
     
# start the color sensor
##_TRIG=5 # trigger pin on the HC-SR04
##_ECHO=6 # echo pin
##_COLOUR_OUT       = 19
##_COLOUR_FILTER_S2 = 13
##_COLOUR_FILTER_S3 = 26
##_COLOUR_FREQ_S0   = 16
##_COLOUR_FREQ_S1   = 12
##_COLOUR_LED       = 21

MyScene=display(title='Virtual World with distance sensor') #Create your scene and give it a title.

MyScene.width=800  #We can set the dimension of your visual box. 800X800 pixels works well on my screen
MyScene.height= 800
MyScene.autoscale=False #We want to set the range of the scene manually for better control. Turn autoscale off
MyScene.range = (12,12,12) #Set range of your scene to be 12 inches by 12 inches by 12 inches. 
target=box(length=.1, width=10,height=5, pos=(-2,0,0)) #Create the object that will represent your target (which is a colored card for our project)


myBoxLED=box(color=color.blue,length=.1, width=5,height=5, pos=(-8.5,0,-12))
myTubeLed1=cylinder(color=color.gray(1),pos=(-8.5,-1.8,-13.5), radius=0.5,length=1.0 )
myTubeLed2=cylinder(color=color.gray(1),pos=(-8.5,1.8,-13.5), radius=0.5,length=1.0 )
myTubeLed3=cylinder(color=color.gray(1),pos=(-8.5,-1.8,-10.5), radius=0.5,length=1.0 )
myTubeLed4=cylinder(color=color.gray(1),pos=(-8.5,1.8,-10.5), radius=0.5,length=1.0 )
myTubeLed5=cylinder(color=color.gray(0.1),pos=(-8.5,0,-12), radius=1.2,length=0.5 )

myBoxEnd=box(color=color.blue,length=.1, width=10,height=5, pos=(-8.5,0,0)) #This object is blue base plate of the ultrasonic sensor
myTube2=cylinder(pos=(-8.5,0,-2.5), radius=1.5,length=2.0 ) #One of the 'tubes' in the front of the ultrasonic sensor
myTube3=cylinder(pos=(-8.5,0,2.5), radius=1.5,length=2.0 )  #Other tube
myTube4=cylinder(color=color.black, pos=(-6.6,0,2.5), radius=1.2,length=0.2 )
myTube5=cylinder(color=color.black, pos=(-6.6,0,-2.5), radius=1.2,length=0.2 )
myBoxQuartz=box(color=color.white,length=0.5, width=2, height=0.5, pos=(-8.2,2,0))

myBall=sphere(color=color.red, radius=.3)

lengthLabel = label(pos=(0,7,0), text='Target Distance is: ', box=false, height=20)
##pi = pigpio.pi()
##usSensor = sonar_trigger_echo.ranger(pi,_TRIG,_ECHO)
##colorSensor= TCS3200.sensor(pi,_COLOUR_OUT,\
##                            _COLOUR_FILTER_S2,\
##                            _COLOUR_FILTER_S3,\
##                            _COLOUR_FREQ_S0,\
##                            _COLOUR_FREQ_S1,\
##                            _COLOUR_LED)
# switch the white LEDs of the color sensor on
##colorSensor.led(pi,pigpio.ON);
##colorSensor.set_frequency(2)
##interval = 0.2
##colorSensor.set_update_interval(interval)

##wait_for_return("Calibrating black object, press RETURN to start")
##for i in range(5):
##  time.sleep(interval)
##  hz = colorSensor.get_hertz()
##  print(hz)
###hz = [61,57,77]
##colorSensor.set_black_level(hz)
##                
##wait_for_return("Calibrating white object, press RETURN to start")
##
##for i in range(5):
##   time.sleep(interval)
##   hz = colorSensor.get_hertz()
##   print(hz)
##
###hz = [281,269,355]
##colorSensor.set_white_level(hz)
##
##time.sleep(interval)
##
##rgb = colorSensor.get_rgb()
##print "Color: ",
##print rgb
##r=0
##
##while True:
##    rgb = colorSensor.get_rgb()
##    vPythonColor=[0,0,0]
##    vPythonColor[0]=rgb[0]/255.0
##    vPythonColor[1]=rgb[1]/255.0
##    vPythonColor[2]=rgb[2]/255.0    
##    print "Color: ",
##    print vPythonColor
##    
##    measurement = usSensor.read()
##    distance = measurement/1000000.0 * 17150
##    if distance < 6:
##      target.color=vPythonColor
##    print("{} {} {} cm".format(r, measurement, distance))
##    myLabel = "Target distance is: " + "{:04.2f}".format(distance) + " cm"
##    r += 1
##    print "x-pos:" + str(-8.5 + distance)
##    lengthLabel.text = myLabel
##    target.pos=(-8.5+distance,0,0)
##    time.sleep(0.1)

