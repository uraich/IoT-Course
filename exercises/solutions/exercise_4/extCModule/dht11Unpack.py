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
print("Unpacking DHT11 data")
try:
    fd_r = open("dht11.txt","r")
except:
    print("Could not open the file 'dht11.txt' for reading, giving up ...")
    sys.exit()

try:
    fd_w = open("dht11Unpacked.txt","w")
except:
    print("Could not open the file 'dht11.dat' for writing, giving up ...")
    fd_r.close()
    sys.exit()

#d = int(fd_r.readline(),base=16)
#print("value read: %08x"%d)

for i in range(32):
    d=int(fd_r.readline(),base=16)
    print("value read: %08x"%d)
    mask = 0x80000000
    for j in range(32):
        if d & mask:
            fd_w.write(str(1)+'\n')
        else:
            fd_w.write(str(0)+'\n')
        mask = mask >> 1

fd_r.close()
fd_w.close()
            





