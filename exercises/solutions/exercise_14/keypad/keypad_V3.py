# keypad driver
# Interrupt driven keypad scan routine.
# When a button is pressed the key value is saved in a circular buffer
# copyright U. Raich, 21.1.2021
# The program is part of an IoT course at the University of Cape Coast, Ghana
# released under GPL

from machine import Pin
from time import sleep_us,sleep_ms
from circular_buffer import CircularBuffer

class KeyPad:
    chars = [['1','2','3','A'],['4','5','6','B'],
             ['7','8','9','C'],['*','0','#','D']]
    
    def key_change(self,src):
        # print("key changed on col ",src, end=" ")
        # a key has been pressed, do a scan to find out which one
        # print("value: ",src.value())
        # if src.value() == 1:
        #     return
        for i in range(4):
            if src == self.cols[i]:
                col_found = i
                # print("col: ",i)
        src.irq(handler = None)
        cnt = 0
        for row in range(4):
            self.rows[row].on()
            if src.value() == 1:
                cnt +=1
                # print("row: ",row)
                row_found = row
                self.rows[row].off()
        # print("cnt: ",cnt)
        if cnt == 1:
            # print("button found: ",self.chars[row_found][col_found])
            self.cb.write(self.chars[row_found][col_found])
        src.irq(handler=self.key_change)
            
            
    def __init__(self,row1=23,row2=19,row3=18,row4=26,
                 col1=16,col2=17,col3=21,col4=22):
        self.rows = [None]*4
        self.cols = [None]*4
        
        self.cb = CircularBuffer(32)
        
        self.row_pins = [row1,row2,row3,row4]
        self.col_pins = [col1,col2,col3,col4]
        for i in range(4):
            print("self.rows[%d]: %d"%(i,self.row_pins[i]))
        for i in range(4):
            print("self.cols[%d]: %d"%(i,self.col_pins[i]))

        # set all pins to input with pull_up
        for row in range(4):
            self.rows[row]=Pin(self.row_pins[row],Pin.OUT)
            self.rows[row].off()    # set the level to zero
        for col in range(4):
            self.cols[col]=Pin(self.col_pins[col],Pin.IN,Pin.PULL_UP)
            self.cols[col].irq(handler=None)
            self.cols[col].irq(trigger=Pin.IRQ_FALLING,handler=self.key_change)


keypad = KeyPad()
print("Reading keypad")
for i in range(10):
    while keypad.cb.available():
        print(keypad.cb.read())
    sleep_ms(5000)
    
    
            
