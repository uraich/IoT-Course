#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License

import sys

def parse(inText):
    global value1,value2
    valueStrings = inText.split()
    
#   print(valueStrings, len(inText))
    # check if exactly 2 values have been entered
    if (len(valueStrings) != 2):
        print("Please enter exactly 2 integer values")
        return False
    # convert first value
    value1 = int(valueStrings[0])        
    # convert second value
    value2 = int(valueStrings[1])
    return True

global value1,value2

while True:
    print("Please enter two integer numbers separated by a space: ",end="")
    inText = input()
    if (parse(inText)):
        if value1<value2:
            print("The first number is smaller than the second")
        elif value1 == value2:
            print("The first value and the second are equal")
        else:
            print("The first value is bigger than the second")
        print("because value 1 is %d and value 2 is %d"%(value1,value2))
        sys.exit()
    else:
        print("Bad input!")

