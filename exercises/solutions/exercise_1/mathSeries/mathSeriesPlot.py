#!/bin/python3
# Test the mathSeries class
# Solution to exercise 1 of the course on the Internet of Things
# at the Univerity of Cape Coast, Ghana
# Copyright (c) U. Raich, May 2020
#
import mathSeries
import matplotlib.pyplot as plt

series = mathSeries.MathSeries()
print("----------------------------------------------------------------------")
print("Fibonacci numbers up to F(24):")
fibs = series.fibonacci(24)
print(fibs)

#plot

fig, ax = plt.subplots()
ax.set(xlabel="n",ylabel="sum or product",title="  Factorial up to 10 and Fibonacci Numbers up to F(24)")
ax.plot(fibs,'g',label="Fibonacci Numbers up to F(24)")
ax.grid()

fibs = series.fibonacci_max(100000)
print("----------------------------------------------------------------------")
print("Fibonacci numbers up to 100000:")
print(fibs)

n=10
print("----------------------------------------------------------------------")
fact=series.factorial(n)
#print("Factorial of 8: ",series.factorial(n))
print("Factorial of 10: ",fact[n-1])
print("Length of fact: ",len(fact))

# plot the factorials

ax.plot(range(1,len(fact)+1),fact,'r',label="Factorial up to 10")
ax.legend()
plt.savefig("factFibonacci.png")
#plt.show()

n=50
base=2
print("----------------------------------------------------------------------")
print("Geometric number series: ",end="")
geo = series.geometric(n,base)
print(geo[n-1])

# plot the series

fig, ax = plt.subplots()
ax.set(xlabel="x",ylabel="n",title="Geometric and Harmonic number series")
ax.plot(geo,'g',label="Geometric number series")
#plt.show()

print("----------------------------------------------------------------------")
print("Harmonic number series: ",end="")
harm=series.harmonic(n)
print(harm[len(harm)-1])
print("----------------------------------------------------------------------")

# plot

#print("Length of harm series: ",len(harm))
ax.plot(range(1,len(harm)+1),harm,'r',label="Harmonic number series")
ax.legend()
ax.grid()
#plt.show()

print("Approximation of e: ",end="")
e=series.eulerSeries(n)
print(e[n-1])

fig, ax = plt.subplots()
ax.set_title("Approximations of ln(2), e and pi")
ax.set(xlabel="n",ylabel="approximation",title="Approximation of pi,e,ln(2)")
ax.plot(e,'g',label="Approximation of Euler's number e")

print("----------------------------------------------------------------------")
print("Approximation of pi with Gregory-Leibniz series: ",end="")
gl = series.piSeries(n)
#print(series.pi(n))
print(gl[len(gl)-1])
print("----------------------------------------------------------------------")

# plot

ax.plot(gl,'r',label="Approximation of pi with Gregory Leibniz series")

print("Approximation of pi with Wallis series: ",end="")
w=series.wallisSeries(n)

# the Wallis series approximates pi/2

for i in range(len(w)):
    w[i] *= 2;
#print(series.wallis(n))
print(w[n-2])
ax.plot(w,'c',label="Approximation of pi with Wallis series")

print("----------------------------------------------------------------------")

print("Approximation of ln(2):",end="")
ln2 = series.ln_twoSeries(n)
#print(series.ln_two(n))
print(ln2[n-1])
print("----------------------------------------------------------------------")

ax.plot(ln2,'b',label="Approximation of ln(2)")

ax.legend()
ax.grid()

plt.show()
