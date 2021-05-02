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

operatorString = ' *[\+,\-,\*,/] *'

opRegEx = re.compile(operatorString)

while True:
    print("Please enter the operator: ",end="")
    calc=input()
    print(calc)
    opMatch=opRegEx.match(calc)
    print(opMatch)
    if opMatch:
        print("Groups: ",opMatch.groups())
    else:
        print("No match")
