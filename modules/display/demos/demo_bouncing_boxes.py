"""ST7735 demo (bouncing boxes)."""
from machine import Pin, SPI
from random import random, seed
from ST7735 import Display, color565
from utime import sleep_us, ticks_cpu, ticks_us, ticks_diff
import sys

if sys.platform == 'esp8266':
    print('1.4 inch TFT screen test on ESP8266')
    SPI_CS = 16
    SPI_DC = 15
    spi = SPI(1)
    
elif sys.platform == 'esp32':
    print('1.4 inch TFT screen test on ESP32')
    sck = Pin(18)
    miso= Pin(19)
    mosi= Pin(23)
    SPI_CS = 26
    SPI_DC = 5
    spi = SPI(2, baudrate=32000000, sck=sck, mosi=mosi, miso=miso)


class Box(object):
    """Bouncing box."""

    def __init__(self, screen_width, screen_height, size, display, color):
        """Initialize box.

        Args:
            screen_width (int): Width of screen.
            screen_height (int): Width of height.
            size (int): Square side length.
            display (SSD1351): OLED display object.
            color (int): RGB565 color value.
        """
        self.size = size
        self.w = screen_width
        self.h = screen_height
        self.display = display
        self.color = color
        # Generate non-zero random speeds between -5.0 and 5.0
        seed(ticks_cpu())
        r = random() * 10.0
        self.x_speed = 5.0 - r if r < 5.0 else r - 10.0
        r = random() * 10.0
        self.y_speed = 5.0 - r if r < 5.0 else r - 10.0

        self.x = self.w / 2.0
        self.y = self.h / 2.0
        self.prev_x = self.x
        self.prev_y = self.y

    def update_pos(self):
        """Update box position and speed."""
        x = self.x
        y = self.y
        size = self.size
        w = self.w
        h = self.h
        x_speed = abs(self.x_speed)
        y_speed = abs(self.y_speed)
        self.prev_x = x
        self.prev_y = y

        if x + size >= w - x_speed:
            self.x_speed = -x_speed
        elif x - size <= x_speed + 1:
            self.x_speed = x_speed

        if y + size >= h - y_speed:
            self.y_speed = -y_speed
        elif y - size <= y_speed + 1:
            self.y_speed = y_speed

        self.x = x + self.x_speed
        self.y = y + self.y_speed

    def draw(self):
        """Draw box."""
        x = int(self.x)
        y = int(self.y)
        size = self.size
        prev_x = int(self.prev_x)
        prev_y = int(self.prev_y)
        self.display.draw_filledRectangle(prev_x - size,
                                prev_y - size,
                                size, size, 0)
        self.display.draw_filledRectangle(x - size,
                                y - size,
                                size, size, self.color)


def test():
    """Bouncing box."""
    display=Display(spi,SPI_CS,SPI_DC)
    try:

        display.clear()

        colors = [color565(255, 0, 0),
                  color565(0, 255, 0),
                  color565(0, 0, 255),
                  color565(255, 255, 0),
                  color565(0, 255, 255),
                  color565(255, 0, 255)]
        sizes = [12, 11, 10, 9, 8, 7]
        boxes = [Box(128, 128, sizes[i], display,
                 colors[i]) for i in range(6)]

        while True:
            timer = ticks_us()
            for b in boxes:
                b.update_pos()
                b.draw()
            # Attempt to set framerate to 30 FPS
            timer_dif = 33333 - ticks_diff(ticks_us(), timer)
            if timer_dif > 0:
                sleep_us(timer_dif)

    except KeyboardInterrupt:
        display.cleanup()

test()
