#
# Try the dht11Raw module
#
# Copyright (c) U. Raich 10.3.2020
#
import array
import dht11Raw
from machine import Pin
import uerrno as errrno
import uos

#initialize the array to 32 zeros
dht11Data =  array.array("I",[0]*32)

# check if the data directory exists, if not, create it
try:
    uos.stat("/data")
except OSError as e:
    if len(e.args) > 0 and e.args[0] == errno.ENOENT:
        print("/data does not exist, creating it")
        uos.mkdir("/data")
        
# open the file /data/dht11.txt

f = open("/data/dht11.txt","w")
pin = Pin(16)

dht11Raw.dht11ReadRaw(pin,dht11Data)

for i in range(32):
    # the 'new' way of formatting the number
    dataString = '0x{:08x}\n'.format(dht11Data[i])
    # the 'old' way of formatting
    # dataString="0x%08x"%dht11Data[i]
    f.write(dataString)
f.close()
