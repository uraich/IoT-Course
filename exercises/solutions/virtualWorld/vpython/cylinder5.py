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
paper = box(pos=vector(1,0,0), length=0.1, width=5)
# now we move the paper in steps of 0.5 mm
paper_pos = paper.pos
while True:
    for i in range(4*16):
        paper_pos.x = i/16
        time.sleep(0.2)
    for i in range(4*16):
        paper_pos.x = 4-i/16
        paper.pos = paper_pos
        time.sleep(0.2)
