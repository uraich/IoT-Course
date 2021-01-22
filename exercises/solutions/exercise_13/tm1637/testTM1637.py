from tm1637 import TM1637
from time import sleep_ms
tm1637 = TM1637()
tm1637.log.debug("display on")
tm1637.display_on()
tm1637.log.debug("write_display 0 with 1")
tm1637.write_digit(0,1)
tm1637.write_digit(1,2,True)
tm1637.write_digit(2,3)
tm1637.write_digit(3,4)
colon = False
for _ in range(10):
    tm1637.write_digit(0,1)
    tm1637.write_digit(1,2,colon)
    tm1637.write_digit(2,3)
    tm1637.write_digit(3,4)
    sleep_ms(1000)
    colon = not colon
    
for _ in range(10):
    tm1637.clear_digits(colon)
    sleep_ms(1000)
    colon = not colon
    
tm1637.write_digit(0,8)
tm1637.write_digit(1,8,colon)
tm1637.write_digit(2,8)
tm1637.write_digit(3,8)
sleep_ms(1000)

tm1637.write_hex(0xaffe)
sleep_ms(1000)

tm1637.write_dec(5678)
sleep_ms(1000)

tm1637.clear_digits()
#
#tm1637.log.debug("Test brightness")
#for i in range(8):
#    tm1637.brightness(i)


if tm1637.debug:
    f = open("/data/dio.txt","w+b")
    f.write(tm1637.dio_data)
    f.close()
        
    f = open("/data/clk.txt","w+b")
    f.write(tm1637.clk_data)
    f.close()
