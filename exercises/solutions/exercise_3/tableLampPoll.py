from utime import sleep_ms
import sys
from machine import Pin

USER_LED_PIN = 2
BUTTON_PIN   = 22 
led = Pin(USER_LED_PIN, Pin.OUT)        
button = Pin(BUTTON_PIN, Pin.IN,Pin.PULL_UP)

led_state = False
led.value(led_state)

print("Push the button to switch the table lamp on")
print("Push the button a second time to switch it off again")
while True:
    try:
        if not button.value():
            # wait to debounce
            sleep_ms(20)
            if not button.value():
                led_state = not led_state
                led.value(led_state)
                # wait for the switch to be released
                while not button.value():
                    # wait to debounce
                    sleep_ms(20)
    except KeyboardInterrupt:
        led.off()
        sys.exit()
              
