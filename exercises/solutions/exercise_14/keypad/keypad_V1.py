# keypad driver
# The driver reads the 16 button keypad
# It scans the kex matrix every 100 ms and prints which switch is closed. 
# copyright U. Raich, 21.1.2021
# The program is part of an IoT course at the University of Cape Coast, Ghana
# released under GPL

from machine import Pin
from time import sleep_us,sleep_ms

class KeyPad:
    chars = [['1','2','3','A'],['4','5','6','B'],
             ['7','8','9','C'],['*','0','#','D']]
    
    def __init__(self,row1=23,row2=19,row3=18,row4=26,
                 col1=16,col2=17,col3=21,col4=22):
        self.rows = [None]*4
        self.cols = [None]*4
        
        self.row_pins = [row1,row2,row3,row4]
        self.col_pins = [col1,col2,col3,col4]
        for i in range(4):
            print("self.rows[%d]: %d"%(i,self.row_pins[i]))
        for i in range(4):
            print("self.cols[%d]: %d"%(i,self.col_pins[i]))

        # set all pins to input wil pull_up
        for i in range(4):
            self.rows[i]=Pin(self.row_pins[i],Pin.IN,Pin.PULL_UP)
            self.cols[i]=Pin(self.col_pins[i],Pin.IN,Pin.PULL_UP)

    def scan(self):
        print("Start scan")
        while True:
            for row in range(4):
                # put a low on the row
                self.rows[row] = Pin(self.row_pins[row],Pin.OUT)
                self.rows[row].off()
                for col in range(4):
                    if self.cols[col].value() == 0:
                        print("Char: " + self.chars[row][col])
                # switch the row back to input mode
                self.rows[row] = Pin(self.row_pins[row],Pin.IN,Pin.PULL_UP)
                sleep_ms(10)
            sleep_ms(100)

keypad = KeyPad()
keypad.scan()
            
