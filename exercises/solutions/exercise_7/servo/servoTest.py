# control a cheap amd simple servo motor through PWM

from machine import Pin,PWM
import time

_SERVO_PIN=26

servo=PWM(Pin(_SERVO_PIN))
servo.freq(50) # servo motor require 50 Hz frequency
for i in range(35,135):
    servo.duty(i)
    time.sleep(0.01)

for i in range(135,40,-1):
    servo.duty(i)
    time.sleep(0.01)
