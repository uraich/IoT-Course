from tm1637 import TM1637
from time import sleep_ms
tm1637 = TM1637()
tm1637.debug=True
tm1637.start_transfer()
tm1637.write_byte(0x55)
tm1637.stop_transfer()

if tm1637.debug:
    f = open("/data/dio.txt","w+b")
    f.write(tm1637.dio_data)
    f.close()
        
    f = open("/data/clk.txt","w+b")
    f.write(tm1637.clk_data)
    f.close()
