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

paperColor=[0,0,0]
red   = 0
green = 1
blue  = 2
input("start color changes")
# color changes
while True:
   for color in range(512):
      paperColor= vector((color >> 6)/ 8.0,(color >> 3 & 7) / 8.0, (color & 7)/ 8.0)
      paper.color = paperColor
      time.sleep(0.05)
                

