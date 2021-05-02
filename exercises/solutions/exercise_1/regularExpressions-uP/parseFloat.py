#!/usr/bin/python3
#
# try regular expressions to provide a parser for the calculator
#

# a float number is composed of
# 0 or more spaces followed by
# 0 or 1 minus sign followed by
# one '.' followed by 1 or more digits or
# one or more digits followed by 0 or 1 '.' followed by 0 or more digits

# the operator is composed of 0 or more spaces followed be one of +,-,*,/
# The calculation if a float followed by an operator followed by a float

import re

floatString='( *[+,-]?((\.\d+)|(\d+\.*\d*)) *)'
print(floatString)
floatRegEx = re.compile('^'+floatString+'$')
print(floatRegEx)
while True:
    print("Please enter a floating point number: ",end="")
    float=input()
    floatMatch=floatRegEx.match(float)
    print(floatMatch)
    if floatMatch:
        print("Match")
        print(floatMatch.group(2))
    else:
        print("No match")
