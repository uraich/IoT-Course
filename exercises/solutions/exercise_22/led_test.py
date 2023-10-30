# led_test.py: Check toggling the LED on the ESP32-S3 using a timer
# Copyright (c) U. Raich October 2023
# This program is part of the TinyML course at the
# University of Cape Coast, Ghana

from machine import Pin,Timer
from neopixel import NeoPixel
from utime import sleep_ms

LED_PIN = 47
LED_INTENSITY = 0x1f

class BLE_led():
    def __init__(self):
        self.state = False
        self.led = NeoPixel(Pin(LED_PIN),1)

    def led_off(self):
        # switch LED off
        self.led[0] = (0,0,0)
        self.led.write()
        self.state = False

    def led_on(self):
        # switch LED on (blue color)
        self.led[0] = (0,0,LED_INTENSITY)
        self.led.write()
        self.state = True

    def toggle(self):
        if self.state:
            self.led_off()
        else:
            self.led_on()

def toggleLED(src):
    led.toggle()
    
led = BLE_led()
timer = Timer(0)
timer.init(period=100,mode=Timer.PERIODIC, callback= toggleLED)






