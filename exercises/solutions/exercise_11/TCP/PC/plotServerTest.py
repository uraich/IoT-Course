#!/usr/bin/python3
from matplotlib import pyplot as plt
from collections import deque
import random,time

# parses a message returning the parameter names and values
# a message has the form:
# par_name1 [unit]: value1, par_name2 [unit]: value2, ... 
def parse(msg):
    par_names = []
    par_values = []
    measParts = msg.split(",")
    print(measParts)
    for i in range(len(measParts)):
        tmp = measParts[i].split(":")
        par_names.append(tmp[0])
        try:
            val = float(tmp[1])
            par_values.append(val)
        except:
            print("measage " + msg + "does not have the required form")
            return None,None
    print(par_names)
    print(par_values)
    return par_names,par_values

def plot(msg):
    names,values = parse(msg)
    if not names:
        return
    # check if the queues have already been created
    # create them if not
    if len(queues) == 0:
        for i in range(len(names)):
            queues.append(deque(maxlen=100))
    # clear the plot
    plt.clf()
    for i in range(len(names)):
        queues[i].append(values[i])   # add the value to the ring buffer
        # plot the points
        plt.plot(queues[i],label=names[i])
        plt.scatter(range(len(queues[i])),queues[i])
    
    title = ""
    for i in range(len(names)):
        title += names[i] +" "
    plt.title(title)
    plt.legend(loc="upper right")
    plt.draw()
    plt.pause(0.01)
    
queues = []

for i in range(199):
    temp =  random.random()
    humi = random.random()
    msg = "temperature [°C]: {:f},humidity [%]: {:f}".format(temp,humi)
    plot(msg)
    time.sleep(0.5)
               
