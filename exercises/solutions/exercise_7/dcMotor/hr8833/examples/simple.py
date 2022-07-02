# simple.py: a simple Lolin motor shield test
# This is a port from the Lolin Arduino code https://github.com/wemos/LOLIN_I2C_MOTOR_Library
# to MicroPython.
# Author: U. Raich
# This code is part of the course on the Internet of Things at the
# University of Cape Coast, Ghana

from dc_motor import HR8833
from utime import sleep_ms

print("Motor Shield Testing...")
motor = HR8833(debug=False)
motor.reset()
info = motor.getInfo()
print("Product ID: 0x{:02x}, firmware version: 0x{:02x}".format(info[0],info[1]))

print("Change A to CCW, B to CW, Freq: 1000Hz")
print("Duty Testing...")

motor.changeFreq(motor.CH_BOTH, 1000) # Change A & B 's Frequency to 1000Hz.
motor.changeStatus(motor.CH_A, motor.STATUS_CCW)
motor.changeStatus(motor.CH_B, motor.STATUS_CW)

for duty in range(101) :
    motor.changeDuty(motor.CH_A, duty)
    motor.changeDuty(motor.CH_B, 100 - duty)
    
    print("Change channel A Duty to {:d} %".format(duty))
    print("Change channel B Duty to {:d} %".format(100-duty))
    sleep_ms(100)

print("STANDBY Testing...")
motor.changeStatus(motor.CH_BOTH, motor.STATUS_CCW)
motor.changeDuty(motor.CH_BOTH, 100)
for i in range(5) :
    print("MOTOR_STATUS_STANDBY")
    motor.changeStatus(motor.CH_BOTH, motor.STATUS_STANDBY)
    sleep_ms(500)
    print("MOTOR_STATUS_CW")
    motor.changeStatus(motor.CH_BOTH, motor.STATUS_CW)
    sleep_ms(500)
    print("MOTOR_STATUS_STANDBY")
    motor.changeStatus(motor.CH_BOTH, motor.STATUS_STANDBY)
    sleep_ms(500)
    print("MOTOR_STATUS_CCW")
    motor.changeStatus(motor.CH_BOTH, motor.STATUS_CCW)
    sleep_ms(500)

print("MOTOR_STATUS Testing...")
for i in range(5) :
    print("MOTOR_STATUS_STOP")
    motor.changeStatus(motor.CH_A, motor.STATUS_STOP)
    sleep_ms(500)
    print("MOTOR_STATUS_CCW")
    motor.changeStatus(motor.CH_A, motor.STATUS_CCW)
    sleep_ms(500)
    print("MOTOR_SHORT_BRAKE")
    motor.changeStatus(motor.CH_A, motor.STATUS_SHORT_BRAKE)
    sleep_ms(500)
    print("MOTOR_STATUS_CW")
    motor.changeStatus(motor.CH_A, motor.STATUS_CW)
    sleep_ms(500)
motor.changeDuty(motor.CH_BOTH, 0)