#!/usr/bin/env python3
# demonstrate the try/except statement
# we divide a number and check for divide by zero exceptions
#

for i in range(-5,5,1):
    try:
        print("10 / %d = %f"%(i,10/i))
    except ZeroDivisionError:
        print("Cannot divide by zero")


