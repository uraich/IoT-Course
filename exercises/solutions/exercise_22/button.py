# button.py: Connects an interrupt to the button on GPIO 0 and toggles
# the LED on the ESP32S3 when the button is pressed.
# Copyright (c) U. Raich October
# This program is part of the TinyML course at the
# University of Cape Coast, Ghana
# It is released under the MIT Licence

from machine import Pin
from neopixel import NeoPixel
from utime import sleep
import sys

LED_PIN = 47
LED_INTENSITY = 0x1f

class BLE_led():
    def __init__(self):
        self.state = False
        self.led = NeoPixel(Pin(LED_PIN),1)
        self.led_off()

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

button = Pin(0,Pin.IN)
led = BLE_led()

def button_irq(pin):
    led.toggle()

button.irq(trigger=Pin.IRQ_FALLING, handler=button_irq)

try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    led.led_off()
    sys.exit()
