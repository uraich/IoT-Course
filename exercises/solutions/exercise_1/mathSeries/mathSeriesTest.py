#!/bin/python3
# Test the mathSeries class
# Solution to exercise 1 of the course on the Internet of Things
# at the Univerity of Cape Coast, Ghana
# Copyright (c) U. Raich, May 2020
#
import mathSeries

n=20
series = mathSeries.MathSeries()
print("----------------------------------------------------------------------")
print("Fibonacci numbers up to F(",n,"):")
fibs = series.fibonacci(20)
print(fibs)

fibs = series.fibonacci_max(100000)
print("----------------------------------------------------------------------")
print("Fibonacci numbers up to 100000:")
print(fibs)
n=10
print("----------------------------------------------------------------------")
fact = series.factorial(n)
#print("Factorial(",n,": ")
#print(fact)
#print("Factorial of 10: ",series.factorial(n))
print("Factorial of",n,": ",fact[len(fact)-1])

n=500
base=2
print("----------------------------------------------------------------------")
print("Geometric number series, n=",n,": ",end="")
geo = series.geometric(n,base)
#print(geo)
print(geo[len(geo)-1])

print("----------------------------------------------------------------------")
print("Harmonic number series, n=",n,": ",end="")
harm = series.harmonic(n)
#print(harm)
print(harm[len(harm)-1])

n=100
print("----------------------------------------------------------------------")
print("Approximation of e, n=",n,": ",end="")
e=series.eulerSeries(n)
#print(series.euler(n))
print(e[len(e)-1])

print("----------------------------------------------------------------------")
print("Approximation of pi with Gregory-Leibniz series, n=",n,": ")
p=series.piSeries(n)
#print(series.pi(n))
print(p[len(p)-1])
print("----------------------------------------------------------------------")

print("Approximation of pi with Wallis series, n=",n,": ")
w=series.wallisSeries(n)
#print(series.wallis(n))
print(2*w[len(w)-1])
print("----------------------------------------------------------------------")

print("Approximation of ln(2), n=",n," :",end="")
ln2=series.ln_twoSeries(n)
#print(series.ln_two(n))
print(ln2[len(ln2)-1])

print("----------------------------------------------------------------------")
print("Approximation of e, n=",n,": ",end="")
e=series.euler(n)
#print(series.euler(n))
print(e)

n=1000000
print("----------------------------------------------------------------------")
print("Approximation of pi with Gregory-Leibniz series, n=",n,": ")
pi=series.pi(n)
#print(series.pi(n))
print(pi)
print("----------------------------------------------------------------------")

print("Approximation of pi with Wallis series, n=",n,": ")
w=series.wallis(n)
#print(series.wallis(n))
print(2*w)
print("----------------------------------------------------------------------")

print("Approximation of ln(2), n=",n," :",end="")
ln2=series.ln_two(n)
#print(series.ln_two(n))
print(ln2)
print("----------------------------------------------------------------------")
