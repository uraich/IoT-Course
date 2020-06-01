#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License
# Demonstrates the Fibonacci number series

a,b = 0,1

print("Please enter the maximum number: ",end="")

def getMaxNum():
    while True:
        try:
            numString = input()
            maxNum=int(numString)
        except ValueError:
            print(numString," is not an integer number, please give a new one: ",end="")
            getMaxNum()
        
        return maxNum
        
maxNum = getMaxNum()
print(maxNum)
print("%d %d"%(a,b),end=" ")
while True:
    c=a+b
    print(c,end=" ")
    a=b
    b=c
    if a+b > maxNum:
        break
print("")
