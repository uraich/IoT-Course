#!/usr/bin/python3
# Unpack the dht11 data which are packed into 32bit words into individual bits
# and write these to a file
# The file can then be plotted with gnuplot
# Copyright (c) U. Raich 10.3.2020
# This program was written for the course on embedded systems at the
# University of Cape Coast, Ghana
# It is released under GPL
#

# open the file with the packed data which must be named: "dht11.txt"

import sys
import matplotlib.pyplot as plt

#print("Unpacking DHT11 data")
try:
    fd_r = open("dht11.txt","r")
except:
    print("Could not open the file 'dht11.txt' for reading, giving up ...")
    sys.exit()

bits=[]
x=range(0,1024*4,4)
for i in range(32):
    d=int(fd_r.readline(),base=16)
#    print("value read: %08x"%d)
    mask = 0x80000000
    for j in range(32):
        if d & mask:
            bits.append(1)
        else:
            bits.append(0)
        mask = mask >> 1

fd_r.close()
print("bits length: %d"%len(bits))
fig, ax = plt.subplots(figsize=(15,5))
ax.set(xlabel='time (us)', ylabel='signal level',
       title='DHT11 protocol')
ax.plot(x,bits)
ax.grid()

plt.show()




