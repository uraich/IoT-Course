#!/usr/bin/python3
import matplotlib.pyplot as plt
from collections import deque
import random
# MAX NO. OF POINTS TO STORE
temp = deque(maxlen = 40)
humi = deque(maxlen = 40)
while True:
    # GENERATING THE POINTS - FOR DEMO
    perc = random.random()
    temp.append(perc)
    perc = random.random() + 2
    humi.append(perc)
    
    # PLOTTING THE POINTS
    plt.plot(temp, label='temperature')
    plt.scatter(range(len(temp)),temp)
    
    plt.plot(humi, label='humidity')
    plt.scatter(range(len(humi)),humi)
    
    # SET Y AXIS RANGE
    plt.ylim(-1,4)
    
    # DRAW, PAUSE AND CLEAR
    plt.title("Temperature and Humidity")
    plt.legend()
    plt.draw()
    plt.pause(0.1)
    plt.clf()

