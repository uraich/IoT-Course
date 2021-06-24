from machine import Pin
#
# This is a version of the interrupt driven table lamp without switch debouncing
# Please observe that the lamp works erratically from time to time
# 
class TableLamp:
    USER_LED_PIN = 2
    BUTTON_PIN   = 22
    
    def __init__(self):
        self.current_led_state = False
        self.led = Pin(self.USER_LED_PIN, Pin.OUT)
        # start with led switched off
        self.led.off()
        self.button = Pin(self.BUTTON_PIN, Pin.IN,Pin.PULL_UP)
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_pressed)

    # interrupt service routine started on switch closure    
    def button_pressed(self,int_source):
        self.current_led_state = not  self.current_led_state
        self.led.value(self.current_led_state)


print("Push the button to switch the lamp on")
print("Push it a second time to switch the lamp off again")
table_lamp = TableLamp()
