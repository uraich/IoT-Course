#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License
# Demonstrates the Fibonacci number series

# write the results from the calculations in assignment.py to a file

import sys
# open the file
try:
    fd = open("/tmp/resultFile.txt","w")
except:
    print("Could not open the result file: /tmp/resultFile.txt")
    sys.exit(-1)

a,b = 5,3

plus  = a+b
minus = a-b
mult  = a*b
div   = a/b

fd.write("Results: plus: %d, minus: %d, mult: %d, div: %8.4f"%(plus,minus,mult,div))
fd.close()
