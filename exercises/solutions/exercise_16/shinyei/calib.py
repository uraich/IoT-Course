#!/usr/bin/python3
from math import pow

for i in range(100):
    y = i*0.12
    x = 1.1*pow(y,3)-3.8*pow(y,2)+520*y+0.62
    print(y," ",x)
    
