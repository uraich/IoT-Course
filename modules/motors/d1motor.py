"""
import d1motor
from machine import I2C, Pin
i2c = I2C(Pin(5), Pin(4), freq=100000)
m0 = d1motor.Motor(0, i2c)
m1 = d1motor.Motor(1, i2c)
m0.speed(5000)

"""
import ustruct


_STATE_BRAKE = const(0)
_STATE_RIGHT = const(1) # clockwise
_STATE_LEFT = const(2) # counter-clockwise
_STATE_STOP = const(3)
_STATE_SLEEP = const(4)


class Motor:
    def __init__(self, index, i2c, address=0x30, standby_pin=None):
        if index not in (0, 1):
            raise ValueError("Index must be 0 or 1")
        self.index = index
        self.i2c = i2c
        self.address = address
        self.standby_pin = standby_pin
        self._speed = 0
        self._state = 0
        if standby_pin is not None:
            standby_pin.init(standby_pin.OUT, 0)
        self.frequency(1000)

    def frequency(self, frequency=None):
        if frequency is None:
            return self._pwm_frequency
        self._pwm_frequency = frequency
        self.i2c.writeto_mem(self.address, 0x00 | self.index,
            ustruct.pack(">BH", 0x00, frequency))

    def update(self):
        if self.standby_pin is not None:
            self.standby_pin.value(not self._state == _STATE_SLEEP)
        self.i2c.writeto_mem(self.address, 0x10 | self.index,
            ustruct.pack(">BH", self._state, self._speed))

    def speed(self, speed=None):
        if speed is None:
            return self._speed
        if speed > 0:
            self._speed = min(10000, max(1, speed))
            self._state = _STATE_RIGHT
        elif speed < 0:
            self._speed = min(10000, max(1, -speed))
            self._state = _STATE_LEFT
        else:
            self._speed = 0
            self._state = _STATE_STOP
        self.update()

    def sleep(self):
        self._speed = 0
        self._state = _STATE_SLEEP
        self.update()

    def brake(self):
        self._speed = 0
        self._state = _STATE_BRAKE
        self.update()

