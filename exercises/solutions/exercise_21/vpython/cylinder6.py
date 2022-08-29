#!/usr/bin/python3
# Create a first 3d object with VPython
# import the necessary methods
from vpython import *
import time
# create a cylinder
# change its diameter and length 
cylinder(pos=vector(-5,0,0),axis=vector(4,0,0), radius = 0.5)
# make the sphere really small and change its color
sphere(radius=0.2, color=color.red)
# let's create a virtual paper sheet in form of a very thin box
paper = box(pos=vector(1,0,0), size=vector(0.1,5,5))
# now we move the paper in steps of 0.5 mm
distanceLabel = label(text='Distance to sensor: 0.00 cm',\
                     box=False,pos=vector(0,4,0),color=color.green)
while True:
    for i in range(16):
        paper.pos=vector(i/4.0,0,0)
        distanceLabel.text="Distance to sensor: " + "{:04.2f}".format(i/4.0)\
                            + "cm"
        time.sleep(0.5)
    for i in range(16):
        paper.pos=vector(4-i/4.0,0,0)
        distanceLabel.text="Distance to sensor: " + "{:04.2f}".format(4-i/4.0)\
                            + "cm"
        time.sleep(0.5)
