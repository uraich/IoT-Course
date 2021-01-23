# tm1637 driver test program
# Exercise the tm1637 driver trying all methods of the class
# copyright U. Raich, 20.1.2021
# The program is part of an IoT course at the University of Cape Coast, Ghana
# released under GPLfrom tm1637 import TM1637

from time import sleep_ms
from tm1637 import TM1637

tm1637 = TM1637()
print("demonstrate drawing of segments: only horizontal segments")
for i in range(4):
    tm1637.write_segments(i,0x49)
sleep_ms(1000)
print("Test brightness")
for i in range(8):
    tm1637.set_brightness(i)
    sleep_ms(500)
print("switching display off")
tm1637.display_off()
sleep_ms(1000)
print("switching it on again")
tm1637.display_on()
sleep_ms(1000)

print("display author's name")
U=0x3e
L=0x38
I=0x06
blank = 0
tm1637.write_segments(0,U)
tm1637.write_segments(1,L)
tm1637.write_segments(2,I)
tm1637.write_segments(3,blank)
sleep_ms(1000)

tm1637.write_digit(0,1)
tm1637.write_digit(1,2,True)
tm1637.write_digit(2,3)
tm1637.write_digit(3,4)
print("write 1234 and blink the colon")
colon = False
for _ in range(10):
    tm1637.write_digit(0,1)
    tm1637.write_digit(1,2,colon)
    tm1637.write_digit(2,3)
    tm1637.write_digit(3,4)
    sleep_ms(1000)
    colon = not colon
    
print("clear all digits and blink the colon")    
for _ in range(10):
    tm1637.clear_digits(colon)
    sleep_ms(1000)
    colon = not colon
    
print("switch all segments on including the colon")    
tm1637.write_digit(0,8)
tm1637.write_digit(1,8,colon)
tm1637.write_digit(2,8)
tm1637.write_digit(3,8)
sleep_ms(1000)

print("display hex number")
tm1637.write_hex(0xaffe)
sleep_ms(1000)

print("display decimal number")
tm1637.write_dec(5678)
sleep_ms(1000)

print("clear all digits")
tm1637.clear_digits()

if tm1637.debug:
    f = open("/data/dio.txt","w+b")
    f.write(tm1637.dio_data)
    f.close()
        
    f = open("/data/clk.txt","w+b")
    f.write(tm1637.clk_data)
    f.close()
