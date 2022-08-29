#!/usr/bin/python3
# Create a first 3d object with VPython
# import the necessary methods
from vpython import *
# create a cylinder
# change its diameter and length 
cylinder(pos=vector(-5,0,0),axis=vector(4,0,0), radius = 0.5)
# make the sphere really small and change its color
sphere(radius=0.2, color=color.red)
box(pos=vector(1,0,0), length=0.1, width=5)
