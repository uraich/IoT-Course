from utime import sleep_ms
from machine import Pin,Timer

class TableLamp:
    USER_LED_PIN = 2
    BUTTON_PIN   = 22
    
    def __init__(self):
        self.current_led_state = False
        self.pushed = False
        self.released = False
        self.led = Pin(self.USER_LED_PIN, Pin.OUT)
        # start with led switched off
        self.led.off()
        self.button = Pin(self.BUTTON_PIN, Pin.IN,Pin.PULL_UP)
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_pressed)

        self.timer = Timer(0)

    # interrupt service routine started on switch closure    
    def button_pressed(self,int_source):
        # if we have already seen the new state, it must be switch bouncing
        if self.pushed:
            return
        else:
            # print("pushed")
            self.pushed = True
            # start a 20 ms timer
            self.timer.init(period=20, mode=Timer.ONE_SHOT, callback=self.debounce_push)

    # interrupt service routine started on switch opening
    def button_released(self,int_source):
        if self.released:
            return
        else:
            # print("released")
            self.released = True
            # start a 20 ms timer
            self.timer.init(period=20, mode=Timer.ONE_SHOT, callback=self.debounce_release)            
            
    def debounce_push(self,source):
        # triggered 20 ms after we have seen the switch closure
        self.pushed = False
        self.current_led_state = not self.current_led_state
        self.led.value(self.current_led_state)
        self.button.irq(trigger=Pin.IRQ_RISING, handler=self.button_released)
        
    def debounce_release(self,source):
        # triggered 20 ms after we have seen the switch opening
        self.released = False
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_pressed)

print("Push the button to switch the lamp on")
print("Push it a second time to switch the lamp off again")
table_lamp = TableLamp()
