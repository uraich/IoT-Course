#!/usr/bin/python3
#
# try regular expressions to provide a parser for the calculator
#

# a float number is composed of
# 0 or more spaces followed by
# 0 or 1 minus or plus sign followed by
# one '.' followed by 1 or more digits or
# one or more digits followed by 0 or 1 '.' followed by 0 or more digits
# followed by 0 or more spaces

# the operator is composed of 0 or more spaces followed by one of +,-,*,/
# The calculation is a float followed by an operator followed by a float

# I print the tokens as extracted by the match groups separating the operands
# from the operator by a blanc

import re

floatString='([ ]*[-,+]?(?:(?:[.][\d])|(?:[\d]+[.]?[\d]*))[ ]*)'
operatorString = '([ ]*[\+,\-,\*,/][ ]*)'
calcString = '^'+floatString+operatorString+floatString+'$'
# print(calcString)
floatRegEx = re.compile(floatString)
calcRegEx = re.compile(calcString)

while True:
    print("Please enter the calculation: ",end="")
    calc=input()
    print(calc)
    calcMatch=calcRegEx.match(calc)
    
    if calcMatch:
        # print("Match groups: ",calcMatch.groups())
        try:
            print(calcMatch.group(1)," ",calcMatch.group(2)," ",calcMatch.group(3)," = ",eval(calc))
        except Exception as e:
            if e.__class__ == ZeroDivisionError:
                print("You tried to divide by zero, which is not allowed. Try again")            
    else:
        print("Bad input, please try again")
