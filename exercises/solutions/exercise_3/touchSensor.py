from machine import TouchPad, Pin
from utime import sleep_ms

TOUCH_PIN = 4

tp = TouchPad(Pin(TOUCH_PIN,Pin.IN,Pin.PULL_UP))

while True:
    print("value: ",tp.read())
    sleep_ms(200)
