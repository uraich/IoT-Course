# a simple program to set a register on the I2C bus
from machine import Pin,I2C

i2c = I2C(1,scl=Pin(22),sda=Pin(21))

print("i2c_get: please enter i2c address, register address, values ===> ",end='')

request = input().split()
print(request)

# extract the i2c address

i2c_address = int(request[0])
print("i2c_address: {:02x}".format(i2c_address))

# extract the register address

register_address = int(request[1])
print("register_address: {:02x}".format(i2c_address))

# extract the values and put them into a byte array

no_of_values = len(request)-2
print("Number of values: {:d}".format(no_of_values))
values = bytearray(no_of_values)
for i in range(no_of_values):
      values[i] = int(request[2+i])

# writing data to the register
print("Writing ",end='')
for i in range(len(values)):
    print("0x{:02x} ".format(values[i]),end='')
    
print("to register 0x{:02x} on i2c address: 0x{:02x}".format(register_address,i2c_address))
#i2c.writeto_mem(i2c_address,register_address,values)
