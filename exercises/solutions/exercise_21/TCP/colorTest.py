#!/usr/bin/python3
colorComponent = {'red' : 0,
                   'green': 1,
                   'blue': 2}

colors = [None]*3

colors[colorComponent['red']] = 13
colors[colorComponent['green']] = 23
colors[colorComponent['blue']] = 33
print(colors)
