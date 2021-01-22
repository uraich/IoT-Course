# tm1637 driver
# The driver allows to control a 4 digit seven segment display equipped
# with a tm1637 display driver
# copyright U. Raich, 20.1.2021
# The program is part of an IoT course at the University of Cape Coast, Ghana
# released under GPL

from machine import Pin
from time import sleep_us
D1 = 22  # D1 is connected to GPIO 22
D2 = 21  # D2 is connected to GPIO 21

class TM1637:
    WRITE_DISPLAY = 0x40
    ADDR_AUTO     = 0x40
    ADDR_FIX      = 0x44
    CH0           = 0xc0
    CH1           = 0xc1
    CH2           = 0xc2
    CH3           = 0xc3
    CH4           = 0xc4
    CH5           = 0xc5

    DISPLAY_OFF   = 0x80
    DISPLAY_ON    = 0x88

    def __init__(self, clk_pin=D1, dio_pin=D2):
        self.dio_pin = dio_pin
        self.clk_pin = clk_pin
        self.clk = Pin(clk_pin,Pin.OUT)
        self.dio = Pin(dio_pin,Pin.OUT)
        self.dio.value(1)
        self.clk.value(1)
        self.period=0
        self.dio_data = ''
        self.clk_data = ''
        
    def log(self):
        print("period: %d, clk: %d, dio: %d"%(self.period,self.clk.value(),self.dio.value()))
        for i in range(10):
            self.clk_data += (str(self.clk.value()+1.2)+'\n')
            self.dio_data += (str(self.dio.value())+'\n')
        self.period += 1
        
    def start_transfer(self):
        # to start a transfer set dio high and then pull clock low
        # make sure dio pin is set to output
        print("Start transfer")
        self.log()
        self.clk.value(1)
        self.log()
        sleep_us(50)
        self.dio.value(0)
        self.log()
        sleep_us(50)
        self.clk.value(0)
        self.log()
        print("")
        
    def read_ack(self):
        # switch dio to input in order to see the acknowledge
        self.dio.value(0)
        self.log()
        sleep_us(50)
        #start nineth clock cycle
        self.clk.value(1)
        sleep_us(50)
        print("switch to dio input")
        self.dio = Pin(self.dio_pin,Pin.IN,Pin.PULL_UP)
        acq = self.dio.value() # read the acknowledge bit
        self.log()
 
        self.clk.value(0)
        self.log()
        sleep_us(50)
        self.log()
        sleep_us(50)

        # switch dio back to output
        self.dio = Pin(self.dio_pin,Pin.OUT)
        self.dio.value(0)
        return acq
    
    
    def stop_transfer(self):
        # stop the transfer
        print("stop transfer")
        self.clk.value(1)
        self.log()
        sleep_us(50)
        # pull dio low while clk is high

        self.dio.value(1)
        self.log()
        sleep_us(50)       

    def write_bit(self,bit):
        self.dio.value(bit)
        self.log()
        sleep_us(50)
        self.clk.value(1)
        self.log()
        sleep_us(50)
        self.clk.value(0)
        self.log()
        
    def write_byte(self,data):
        self.start_transfer()
        # transfer the data, bit is clocked on the rising edge of clk
        print("transfer data byte")
        for _ in range(8):
            self.write_bit(data&1)
            data >>= 1
        print("read ack")
        ack = self.read_ack()
        self.stop_transfer()
        print("ack: ",ack)
        
tm1637 = TM1637()
tm1637.write_byte(0x55)
print(tm1637.dio_data)
print(tm1637.clk_data)        
    
    
