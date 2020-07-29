"""ST7735 demo (bouncing sprite)."""
from ST7735 import Display
from machine import Pin, SPI
from utime import sleep_us, ticks_us, ticks_diff
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
    

class BouncingSprite(object):
    """Bouncing Sprite."""

    def __init__(self, path, w, h, screen_width, screen_height,
                 speed, display):
        """Initialize sprite.

        Args:
            path (string): Path of sprite image.
            w, h (int): Width and height of image.
            screen_width (int): Width of screen.
            screen_height (int): Width of height.
            size (int): Square side length.
            speed(int): Initial XY-Speed of sprite.
            display (SSD1351): OLED display object.
            color (int): RGB565 color value.
        """
        self.buf = display.load_sprite(path, w, h)
        self.w = w
        self.h = h
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.display = display
        self.x_speed = speed
        self.y_speed = speed
        self.x = self.screen_width // 2
        self.y = self.screen_height // 2
        self.prev_x = self.x
        self.prev_y = self.y

    def update_pos(self):
        """Update sprite speed and position."""
        x = self.x
        y = self.y
        w = self.w
        h = self.h
        x_speed = abs(self.x_speed)
        y_speed = abs(self.y_speed)

        if x + w + x_speed >= self.screen_width:
            self.x_speed = -x_speed
        elif x - x_speed < 0:
            self.x_speed = x_speed

        if y + h + y_speed >= self.screen_height:
            self.y_speed = -y_speed
        elif y - y_speed <= 0:
            self.y_speed = y_speed

        self.prev_x = x
        self.prev_y = y

        self.x = x + self.x_speed
        self.y = y + self.y_speed

    def draw(self):
        """Draw sprite."""
        x = self.x
        y = self.y
        prev_x = self.prev_x
        prev_y = self.prev_y
        w = self.w
        h = self.h
        x_speed = abs(self.x_speed)
        y_speed = abs(self.y_speed)

        # Determine direction and remove previous portion of sprite
        if prev_x > x:
            # Left
            self.display.fill_rect(x + w, prev_y, x_speed, h, 0)
        elif prev_x < x:
            # Right
            self.display.fill_rect(x - x_speed, prev_y, x_speed, h, 0)
        if prev_y > y:
            # Upward
            self.display.fill_rect(prev_x, y + h, w, y_speed, 0)
        elif prev_y < y:
            # Downward
            self.display.fill_rect(prev_x, y - y_speed, w, y_speed, 0)

        self.display.draw_sprite(self.buf, x, y, w, h)


def test():
    """Bouncing sprite."""

    display=Display(spi,SPI_CS,SPI_DC)
    try:

        display.clear()

        # Load sprite
        logo = BouncingSprite('images/Python41x49.raw',
                              41, 49, 128, 128, 1, display)

        while True:
            timer = ticks_us()
            logo.update_pos()
            logo.draw()
            # Attempt to set framerate to 30 FPS
            timer_dif = 33333 - ticks_diff(ticks_us(), timer)
            if timer_dif > 0:
                sleep_us(timer_dif)

    except KeyboardInterrupt:
        display.cleanup()


test()
