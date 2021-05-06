# IR class
#
# reads the IR remote control through a GPIO pin
# timeList keeps the intervals between signal changes
# ir_bitBuffer keeps the individual bits extracted from the pulse lengths
# read returns the IR code
# The program is based on 23.1_Infrared_Remote.py from the
# Freenove's Python tutorial, which is part of Freenove's ESP32 Ultimate starter kit

# Modifications by U. Raich
# for the IoT course at the Université Cheikh Anta Diop, Dakar, Senegal

from machine import Pin
from utime import ticks_us,ticks_diff,sleep_ms

class IR(object):
    def __init__(self, ir_gpio):
        # define IR data pin as input
        self.irRecv = Pin(ir_gpio, Pin.IN, Pin.PULL_UP)
        # define an interrupt handler that triggers on any state change
        # of the IR data line 
        self.irRecv.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=self.__irInt)
        self.logList = []
        self.index = 0
        self.start = 0

    def __irInt(self, source):
        pulseTime = ticks_us()
        if self.start == 0:
            self.start = pulseTime
            self.index = 0
            return
        self.logList.append(ticks_diff(pulseTime, self.start))
        self.logList
        self.start = pulseTime
        self.index += 1

    def read(self):
        sleep_ms(200) 
        if ticks_diff(
                ticks_us(),
                self.start) > 800000 and self.index > 0:
            self.bitBuffer=[]
            try:
                for i in range(3,66,2):
                    if self.logList[i]>800:
                        self.bitBuffer.append(1)
                    else:
                        self.bitBuffer.append(0)
            except:
                print("IR read error, please try again")
                return
            irValue=0
            # get 32 bits
            if len(self.bitBuffer) < 32:
                print("read error, length of IR buffer is {:d}".format(len(self.bitBuffer)))
                return
            for i in range(0,32):
                irValue=irValue<<1
                if self.bitBuffer[i]==1:
                    irValue |= 1
                    
            # reset
            self.timeList = self.logList
            self.logList = []
            self.index = 0
            self.start = 0
            return irValue

# the main program       

ir = IR(21)
IR_code = {0xff6897 : "0", 0xff30cf : "1", 0xff18e7 : "2", 0xff7a85 : "3", 0xff10ef : "4",
           0xff38c7 : "5", 0xff5aa5 : "6", 0xff42bd : "7", 0xff4ab5 : "8", 0xff52ad : "9",
           0xffa25d : "CH-", 0xff629d : "CH", 0xffe21d : "CH+", 0xff22dd : "|<<", 0xff02fd : "|>>", 0xffc23d : ">||",
           0xffe01f: "-", 0xffa857 : "+", 0xff906f : "EQ", 0xff9867 : "100+", 0xffb04f : "200+"}
while True:
    irValue = ir.read()
    if irValue:
        print("length of timeList: %d"%len(ir.timeList))
        print(ir.timeList)
        print(ir.bitBuffer)
        print(hex(irValue))
        print("key: " + IR_code[irValue])
