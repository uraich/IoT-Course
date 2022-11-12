from machine import Timer,Pin
import time
import uasyncio as asyncio

ledState = False

def cb_timer(timer, led):
 
    ledState=led.value()
    if ledState:
        led.off()
        ledState = False
    else:
        led.on()
        ledState = True
       
class heartbeat:
    def __init__(self,period=5000):
 
        self.period = period
        self.led = Pin(19,Pin.OUT)
        self.tm = Timer(0)

    def enable(self):
        cb = lambda timer: cb_timer(timer, self.led) 
        self.tm.init(period=self.period, callback=cb)

    def disable(self):
        self.tm.deinit()
        self.led.on()
        
