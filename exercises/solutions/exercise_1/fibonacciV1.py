#!/usr/bin/python3
# Demo program originally written in C for the embedded systems course at the
# University of Cape Coast here ported to Python3
# copyright U. Raich 4.3.2020
# This program is released under the Gnu Public License
# Demonstrates the Fibonacci number series

a,b = 0,1
global n

def parse(numString):
    global n
    try:
        n=int(numString)
    except ValueError:
        print(numString," is not an integer number, please give a new one: ")
        return False
    if n < 0:
        print("the \"n\" in F(n) must be > 0 but is ",n)
        return False
    return True
    
while True:
    print("Please enter \"n\" for Fibonacci(n): ",end="")
    numString = input()
    if parse(numString):
        if n == 0:
            print("%d"%a)
            break
        elif n==1:
            print("%d %d"%(a,b))
            break
        else:
            print("%d %d"%(a,b),end=" ")
            for i in range(n-1):
                c = a+b
                print(c,end=" ")
                a=b
                b=c
            print("")
            break;
