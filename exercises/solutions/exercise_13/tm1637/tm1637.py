# tm1637 driver
# The driver allows to control a 4 digit seven segment display equipped
# with a tm1637 display driver
# copyright U. Raich, 20.1.2021
# The program is part of an IoT course at the University of Cape Coast, Ghana
# released under GPL

from machine import Pin
from time import sleep_us,sleep_ms
import ulogging as logging
import sys
D1 = 22  # D1 is connected to GPIO 22
D2 = 21  # D2 is connected to GPIO 21

class TM1637:
    # tms1737 command codes
    TM1637_WRITE_DISPLAY  = 0x40
    TM1637_ADDR_AUTO      = 0x40
    TM1637_ADDR_FIX       = 0x44
    TM1637_CH0            = 0xc0
    TM1637_CH1            = 0xc1
    TM1637_CH2            = 0xc2
    TM1637_CH3            = 0xc3
    TM1637_CH4            = 0xc4
    TM1637_CH5            = 0xc5

    TM1637_DISPLAY_BRIGHT = 0x80
    TM1637_DISPLAY_ON     = 0x88
    TM1637_DISPLAY_OFF    = 0x80
    CLEAR = 16
#
#
#      A
#     ---
#  F |   | B      dp,g,f,e, d,c,b,a: the data byte
#     -G-
#  E |   | C
#     ---
#      D
    hexnums = [0x3f, # 0
               0x06, # 1
               0x5b, # 2
               0x4f, # 3
               0x66, # 4
               0x6d, # 5
               0x7d, # 6
               0x07, # 7
               0x7f, # 8
               0x6f, # 9
               0x77, # A
               0x7c, # b
               0x39, # C
               0x5e, # d
               0x79, # E
               0x71, # F
               0x00] # clear
    
    def __init__(self, clk_pin=D1, dio_pin=D2):
        
        self.digits = [16,16,16,16]
        self.log = logging.getLogger("tm1637")
        self.log.setLevel(logging.ERROR)
        
        self.digits = [16,16,16,16]
        
        self.dio_pin = dio_pin
        self.clk_pin = clk_pin
        self.clk = Pin(clk_pin,Pin.OUT)
        self.dio = Pin(dio_pin,Pin.OUT)
        self.dio.value(1)
        self.clk.value(1)
        
        self.debug=False
        self.period=0
        self.dio_data = ''
        self.clk_data = ''
        
    def log_signal(self):
        if self.debug:
            print("period: %d, clk: %d, dio: %d"%(self.period,self.clk.value(),self.dio.value()))
            for i in range(10):
                self.clk_data += (str(self.clk.value()+1.2)+'\n')
                self.dio_data += (str(self.dio.value())+'\n')
            self.period += 1
        
    def start_transfer(self):
        # to start a transfer set dio high and then pull clock low
        # make sure dio pin is set to output
        self.log.debug("Start transfer")
        self.log_signal()
        self.clk.value(1)
        self.log_signal()
        sleep_us(50)
        self.dio.value(0)
        self.log_signal()
        sleep_us(50)
        self.clk.value(0)
        self.log_signal()
        
    def stop_transfer(self):
        # stop the transfer
        # pull dio high while clk is high
        self.log.debug("stop transfer")
        self.clk.value(1)
        self.log_signal()
        sleep_us(50)

        self.dio.value(0)
        self.log_signal()
        sleep_us(50)
        
        self.dio.value(1)
        self.log_signal()
        sleep_us(50)
        
    def write_bit(self,bit):
        self.dio.value(bit)
        self.log_signal()
        sleep_us(50)
        self.clk.value(1)
        self.log_signal()
        sleep_us(50)
        self.clk.value(0)
        self.log_signal()
        sleep_us(50)
        
    def write_byte(self,data):
        # transfer the data, bit is clocked on the rising edge of clk
        self.log.debug("transfer data byte")
        for _ in range(8):
            self.write_bit(data&1)
            data >>= 1
            
        self.dio.value(0)
        self.log_signal()
        sleep_us(50)                  
        self.dio = Pin(self.dio_pin,Pin.IN,Pin.PULL_UP)
        ack = self.dio.value()
        self.clk.value(1)
        self.log_signal()
        sleep_us(50)        
        self.dio = Pin(self.dio_pin,Pin.OUT)
        self.clk.value(0)
        self.log_signal()
        sleep_us(50)        
        if ack == 1:
            self.log.error("Did not receive acknowledge from tm1637\nAre hardware connections ok?")
        self.log.debug("ack: %d"%ack)
        
    def display_on(self):
        self.start_transfer()
        self.write_byte(self.TM1637_DISPLAY_ON)
        self.stop_transfer()
    
    def write_digit(self,digit_num,digit,colon=True):
       
        if digit < 0 or digit > 0x10:
            self.log.error("digit must be 0..0xf")
            return
        self.digits[digit_num] = digit  # keep current setting of the digit    
        if digit_num < 0 or digit_num > 3:
            self.log.error("digit num must be 0..3")
            return
        # write data to display
        self.start_transfer()
        self.write_byte(self.TM1637_WRITE_DISPLAY)        
        self.stop_transfer()
        
        # write segment codes
        self.start_transfer()
        self.write_byte(self.TM1637_CH0 | digit_num)        
        if digit_num == 1 and colon:
            self.write_byte(self.hexnums[digit] | 0x80)
        else:
            self.write_byte(self.hexnums[digit])
        self.stop_transfer()
        
    def clear_digits(self,colon=False):
        for i in range(4):
            self.write_digit(i,self.CLEAR,colon)
    #
    # write a hex number
    #
    def write_hex(self,number,colon = False):
        if number < 0 or number > 0xffff:
            self.log.error("Value must be an unsigned short")
            return
        for i in range(4):
            self.write_digit(3-i,number&0xf,colon)
            number >>= 4
    #
    # write a decimal number
    #
    def write_dec(self,number,colon=False):
        if number < 0 or number > 9999:
            self.log.error("Value must be 0..9999")
            return
        # get the thousands
        thousands = number // 1000
        number %= 1000
        hundreds = number // 100
        number %= 100
        tens = number//10
        ones = number % 10
        self.log.debug("converted to hex: %d%d%d%d"%(thousands,hundreds,tens,ones))
        bcd = thousands << 12 | hundreds << 8 | tens << 4 | ones
        self.write_hex(bcd,colon)
              
    def brightness(self,value):
        if value < 0 or value > 7:
            self.log.error("Brightness must be 0..7")
        
        self.start_transfer()
        self.write_byte(self.TM1637_DISPLAY_BRIGHT | value)
        self.stop_transfer()
