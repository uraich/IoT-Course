# a simple program to read a register on the I2C bus
# Copyright (c) U. Raich 12.2.2022
# This program is part of the course on IoT at the
# Univesity of Cape Coast, Ghana
# It is released under the MIT license

from machine import Pin,I2C

i2c = I2C(1,scl=Pin(22),sda=Pin(21))

print("i2c_get: please enter i2c address, register address, no of values ===> ",end='')

request = input().split()
print(request)

# extract the i2c address

i2c_address = int(request[0])
print("i2c_address: {:02x}".format(i2c_address))

# extract the register address

register_address = int(request[1])
print("register_address: {:02x}".format(i2c_address))

# extract number of values to be read
no_of_values = int(request[2])

# reading data from the register
values = i2c.readfrom_mem(i2c_address,register_address,no_of_values)

print("Read from register 0x{:02x} on i2c address: 0x{:02x}: ".format(register_address,i2c_address),end='')
for i in range(len(values)):
      print("0x{:02x} ".format(values[i]),end='')
print()
