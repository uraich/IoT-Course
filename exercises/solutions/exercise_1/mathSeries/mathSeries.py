#
# several number series combined in a Python class
# Solution to exercise 1 of the course on the Internet of Things
# at the Univerity of Cape Coast, Ghana
# Copyright (c) U. Raich, May 2020
# 
class MathSeries:
    # prints the Fibonacci series of numbers up to F(n)

    def fibonacci(self,n):
        if n == 0:
            fib = [0]
            return fib
        elif n== 1:
            fib = [0,1]
            return fib
        else:
            a,b = 0,1
            fib = [a,b]
            for i in range(n-1):
                c=a+b
                b=c
                a=b
                fib.append(c)
            return fib
            
    # prints the Fibonacci series of numbers up to a maximum value
    # the number not to be exceeded is given as a parameter
    def fibonacci_max(self,max):
        a,b = 0,1
        fib = [a,b]
 
        while True:
            c=a+b
            fib.append(c)
            a=b
            b=c
            if a+b > max:
                return fib
                break

    # prints the value of factorial(n)
    # n is an integer number

    def factorial(self,n):
        fact = [1]
        f = 1;
        for i in range(2,n+1):
            f *= i
            fact.append(f)
        return fact;

    # same as factorial but calculates and returns only the last
    # value of the series
    def fact(self,n):
        if n == 0:
            return 1
        f=1
        for i in range(1,n+1):
            f *= i
        return f
    
    # Prime numbers
    def prime(self,max):
        p = []
        for n in range(2,max):
            for x in range(2,n):
                if n % x == 0:
                    break
            else:
                p.append(n)
        return p
    
    # the "geometric" number series:
    # 1 + 1/2 + 1/4 + 1/8 + 1/16 ...            
    def geometric(self,n,base):        
        geo = []
        g = 0
        for i in range(n+1):
            g += 1/base**i
            geo.append(g)
        return geo

        # the "geometric" number series:
        # 1 + 1/2 + 1/4 + 1/8 + 1/16 ...

    def harmonic(self,n):        
        g = 0
        harm=[]
        for i in range(1,n+1):
            g += 1/i
            harm.append(g)
        return harm

    def ln_twoSeries(self,n):
        ln2 = []
        sign = 1
        l = 0
        for i in range(1,n+1):
            l += sign*1.0/i
            sign = -sign
            ln2.append(l)
        return ln2
    
    def ln_two(self,n):
        sign = 1
        ln2 = 0
        for i in range(1,n+1):
            ln2 += sign*1.0/i
            sign = -sign
        return ln2
    
    def eulerSeries(self,n):
        eul = []
        e=0
        for i in range(0,n+1):
            e += 1/self.fact(i)
            eul.append(e)
        return eul
    
    def euler(self,n):
        e=0
        for i in range(0,n+1):
            e += 1/self.fact(i)
        return e
    
    def piSeries(self,n):
        pi = [4]
        if n < 0:
            return -1
        if n == 0:
            return pi;
        p=0
        sign = 1
        for i in range(1,n):
            p += sign*4/(2*i-1)
            sign = -sign
            pi.append(p)
        return pi
    
    def pi(self,n):       
        if n < 0:
            return -1
        if n == 0:
            return 4;
        pi=0
        sign = 1
        for i in range(1,n):
            pi += sign*4/(2*i-1)
            sign = -sign
        return pi
    
    def wallisSeries(self,n):
        halfPi =[]
        hpi=1
        for i in range(1,n):
            hpi *= (2*i/(2*i-1)) * (2*i/(2*i+1))
            halfPi.append(hpi)
        return halfPi
    
    def wallis(self,n):
        hpi=1
        for i in range(1,n):
            hpi *= (2*i/(2*i-1)) * (2*i/(2*i+1))

        return hpi
