#
# reads data from the UART in batches
# wait for a timeout to know that the batch is finished
# then sends the data for parsing
#

import machine
import time
u2=machine.UART(2, baudrate=115200, rx=21, tx=22,timeout=100)
buf=bytearray(1024)

while True:
    start = time.ticks_ms()
    noOfBytes = u2.readinto(buf)
    
    if noOfBytes:
        #print("noOfBytes: ",noOfBytes)
        for i in range(noOfBytes):
            print(chr(buf[i]),end="")
        stop = time.ticks_ms()
        print("time to read GPS sentences [ms]: ",stop-start)  
    # start parsing the data

    

