#!/usr/bin/python3
message = "distance: 789.392996, color: 255, 254, 253"
colorComponent = {'red' : 0,
                  'green': 1,
                  'blue': 2}
colors = [None]*3
measurements = message.split(",")
print(measurements)
distance = float(measurements[0].split(' ')[1])
print("distance: {:f}".format(distance))
colors[colorComponent['red']] = int(measurements[1].split(" ")[2])
print("red: 0x{:02x}".format(colors[colorComponent['red']]))
