"""ST7735 OLED module."""
import time
from machine import Pin,SPI
from math import cos, sin, pi, radians, floor
import fonts.sysfont as sysfont
import framebuf
import sys

#60 = 90 right rotation
#C0 = 180 right rotation
#A0 = 270 right rotation
ST7735Rotations = [0x00, 0x60, 0xC0, 0xA0]
ST7735BGR = 0x08 #When set color is bgr else rgb.
ST7735RGB = 0x00

# Command constants from ST7735 datasheet
NOP = 0x0
SWRESET = 0x01
RDDID = 0x04
RDDST = 0x09

SLPIN  = 0x10
SLPOUT  = 0x11
PTLON  = 0x12
NORON  = 0x13

INVOFF = 0x20
INVON = 0x21
DISPOFF = 0x28
DISPON = 0x29
CASET = 0x2A
RASET = 0x2B
RAMWR = 0x2C
RAMRD = 0x2E

COLMOD = 0x3A
MADCTL = 0x36

FRMCTR1 = 0xB1
FRMCTR2 = 0xB2
FRMCTR3 = 0xB3
INVCTR = 0xB4
DISSET5 = 0xB6

PWCTR1 = 0xC0
PWCTR2 = 0xC1
PWCTR3 = 0xC2
PWCTR4 = 0xC3
PWCTR5 = 0xC4
VMCTR1 = 0xC5

RDID1 = 0xDA
RDID2 = 0xDB
RDID3 = 0xDC
RDID4 = 0xDD

PWCTR6 = 0xFC

GMCTRP1 = 0xE0
GMCTRN1 = 0xE1


def color565(r, g, b):
    """Return RGB565 color value.

    Args:
    r (int): Red value.
    g (int): Green value.
    b (int): Blue value.
    """
    # return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3
    return (r & 0xf8 )| (g & 0xe0) >> 5 | (g & 0x1c) << 11 | (b & 0xf8) << 5    
        
def clamp( aValue, aMin, aMax ) :
  return max(aMin, min(aMax, aValue))

class Display(framebuf.FrameBuffer):
    """Serial interface for 16-bit color (5-6-5 RGB) ST7735 OLED display.

    Note:  All coordinates are zero based.
    """
    
    BLACK = 0
    RED = const(0x0fF8)  # (255, 0, 0)
    GREEN = const(0xe007)  # (0, 255, 0)
    BLUE = const(0x1f00)  # (0, 0, 255)
    YELLOW = const(0xe0ff)  # (255, 255, 0)
    FUCHSIA = const(0x1ff8)  # (255, 0, 255)
    AQUA = const(0xff07)  # (0, 255, 255)
    MAROON = const(0x0080)  # (128, 0, 0)
    DARKGREEN = const(0x0004)  # (0, 128, 0)
    NAVY = const(0x1000)  # (0, 0, 128)
    TEAL = const(0x1004)  # (0, 128, 128)
    PURPLE = const(0x1080)  # (128, 0, 128)
    OLIVE = const(0x0084)  # (128, 128, 0)
    ORANGE = const(0x00fc)  # (255, 128, 0)
    DEEP_PINK = const(0x10f8)  # (255, 0, 128)
    CHARTREUSE = const(0xe087)  # (128, 255, 0)
    SPRING_GREEN = const(0xf007)  # (0, 255, 128)
    INDIGO = const(0x180f)  # (128, 0, 255)
    DODGER_BLUE = const(0x1f04)  # (0, 128, 255)
    CYAN = const(0xff87)  # (128, 255, 255)
    PINK = const(0x1ffc)  # (255, 128, 255)
    LIGHT_YELLOW = const(0xf0ff)  # (255, 255, 128)
    LIGHT_CORAL = const(0x10fc)  # (255, 128, 128)
    LIGHT_GREEN = const(0xf087)  # (128, 255, 128)
    LIGHT_SLATE_BLUE = const(0x1f84)  # (128, 128, 255)
    WHITE = const(0xffff)  # (255, 255, 255)
    
    RGB = True
    BGR = False
    def __init__(self, spi, cs, dc, rst=None, width=128, height=128):
        """Initialize OLED.

        Args:
            spi (Class Spi):  SPI interface for OLED
            cs (Class Pin):  Chip select pin
            dc (Class Pin):  Data/Command pin
            rst (Class Pin):  Reset pin
            width (Optional int): Screen width (default 128)
            height (Optional int): Screen height (default 128)
        """
        print("Display with cs: %d, dc: %d"%(cs,dc))
        self.width = width
        self.height = height
        self.xoffset = 2
        self.yoffset = 1
        self.rotate = 0                    #Vertical with top toward pins.
        self._rgb = False                   #color order of bgr.
        self.dc  = Pin(dc, Pin.OUT, Pin.PULL_DOWN)
        if rst == None:
            print("Reset is connected to system reset")
        else:
            print("Reset: %d" % rst)
            self.reset = Pin(rst, Pin.OUT, Pin.PULL_DOWN)
        self.cs = Pin(cs, Pin.OUT, Pin.PULL_DOWN)
        self.cs(1)
        self.spi = spi
        self.colorData = bytearray(2)
        self.windowLocData = bytearray(4)
        
        self.pagesize = self.height // 8
        self.buffer = bytearray(2*self.height * self.width)

        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
            
        # initialize the controller
        
        self.write_cmd(SWRESET)              #Software reset.
        time.sleep_us(150)
        self.write_cmd(SLPOUT)               #out of time.sleep mode.
        time.sleep_us(500)

        data3 = bytearray([0x01, 0x2C, 0x2D])        #fastest refresh, 6 lines front, 3 lines back.
        self.write_cmd(FRMCTR1)              #Frame rate control.
        self.write_data(data3)
        
        self.write_cmd(FRMCTR2)              #Frame rate control.
        self.write_data(data3)
        
        data6 = bytearray([0x01, 0x2c, 0x2d, 0x01, 0x2c, 0x2d])
        self.write_cmd(FRMCTR3)              #Frame rate control.
        self.write_data(data6)
        time.sleep_us(10)
        
        data1 = bytearray(1)
        self.write_cmd(INVCTR)               #Display inversion control
        data1[0] = 0x07                      #Line inversion.
        self.write_data(data1)
        
        self.write_cmd(PWCTR1)               #Power control
        data3[0] = 0xA2
        data3[1] = 0x02
        data3[2] = 0x84
        self.write_data(data3)
        
        self.write_cmd(PWCTR2)               #Power control
        data1[0] = 0xC5   #VGH = 14.7V, VGL = -7.35V
        self.write_data(data1)
        
        data2 = bytearray(2)
        self.write_cmd(PWCTR3)               #Power control
        data2[0] = 0x0A   #Opamp current small
        data2[1] = 0x00   #Boost frequency
        self.write_data(data2)
        
        self.write_cmd(PWCTR4)               #Power control
        data2[0] = 0x8A   #Opamp current small
        data2[1] = 0x2A   #Boost frequency
        self.write_data(data2)
        
        self.write_cmd(PWCTR5)               #Power control
        data2[0] = 0x8A   #Opamp current small
        data2[1] = 0xEE   #Boost frequency
        self.write_data(data2)
        
        self.write_cmd(VMCTR1)               #Power control
        data1[0] = 0x0E
        self.write_data(data1)
        
        self.write_cmd(INVOFF)
        
        self.write_cmd(MADCTL)               #Power control
        data1[0] = 0x08
        self.write_data(data1)
        
        self.write_cmd(COLMOD)
        data1[0] = 0x05
        self.write_data(data1)
        
        self.write_cmd(CASET)                #Column address set.
        self.windowLocData[0] = 0x00
        self.windowLocData[1] = 0x00
        self.windowLocData[2] = 0x00
        self.windowLocData[3] = self.width - 1
        self.write_data(self.windowLocData)
        
        self.write_cmd(RASET)                #Row address set.
        self.windowLocData[3] = self.height - 1
        self.write_data(self.windowLocData)
        
        dataGMCTRP = bytearray([0x0f, 0x1a, 0x0f, 0x18, 0x2f, 0x28, 0x20, 0x22, 0x1f,
                                0x1b, 0x23, 0x37, 0x00, 0x07, 0x02, 0x10])
        self.write_cmd(GMCTRP1)
        self.write_data(dataGMCTRP)
        
        dataGMCTRN = bytearray([0x0f, 0x1b, 0x0f, 0x17, 0x33, 0x2c, 0x29, 0x2e, 0x30,
                                0x30, 0x39, 0x3f, 0x00, 0x07, 0x03, 0x10])
        self.write_cmd(GMCTRN1)
        self.write_data(dataGMCTRN)
        time.sleep_us(10)
        
        self.write_cmd(DISPON)
        time.sleep_us(100)
        
        self.write_cmd(NORON)                #Normal display on.
        time.sleep_us(10)
        
        self.cs(1)
        
    def _setColor( self, color ) :
        self.colorData[0] = color 
        self.colorData[1] = color >> 8
        self.buf = bytes(self.colorData) * 32
        
    def _copy( self, pixels) :
        ''' copy the pixels to the framebuffer '''
        return

    def _draw( self, pixels ) :
        '''Send given color to the device aPixels times.'''

        self.dc(1)
        self.cs(0)
        for i in range(pixels//32):
            self.spi.write(self.buf)
        rest = (int(pixels) % 32)

        if rest > 0:
            buf2 = bytes(self.colorData) * rest
            self.spi.write(buf2)
        self.cs(1)
        
    def _setwindowpoint( self, x,y ) :
        '''Set a single point for drawing a color to.'''
        x = self.xoffset + x
        y = self.yoffset + y
        self.write_cmd(CASET)            #Column address set.
        self.windowLocData[0] = self.xoffset
        self.windowLocData[1] = x
        self.windowLocData[2] = self.xoffset
        self.windowLocData[3] = x
        self.write_data(self.windowLocData)
        
        self.write_cmd(RASET)            #Row address set.
        self.windowLocData[0] = self.yoffset
        self.windowLocData[1] = y
        self.windowLocData[2] = self.yoffset
        self.windowLocData[3] = y
        self.write_data(self.windowLocData)
        self.write_cmd(RAMWR)            #Write to RAM.

    def _setwindowloc( self, x0, y0, x1, y1 ) :
        '''Set a rectangular area for drawing a color to.'''
        self.write_cmd(CASET)            #Column address set.
        self.windowLocData[0] = self.xoffset
        self.windowLocData[1] = self.xoffset + x0
        self.windowLocData[2] = self.xoffset
        self.windowLocData[3] = self.xoffset + x1
        self.write_data(self.windowLocData)
        
        self.write_cmd(RASET)            #Row address set.
        self.windowLocData[0] = self.yoffset
        self.windowLocData[1] = self.yoffset + y0
        self.windowLocData[2] = self.yoffset
        self.windowLocData[3] = self.yoffset + y1
        self.write_data(self.windowLocData)

        self.write_cmd(RAMWR)            #Write to RAM.
        
    def _pushcolor( self, color ) :
        '''Push given color to the device.'''
        self.colorData[0] = color
        self.colorData[1] = color >> 8
        self.write_data(self.colorData)
        
    def write_cmd( self, command, *args ) :
        '''Write given command to the device.'''
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        # Handle any passed data
        if len(args) > 0:
            self.write_data(bytearray(args))
            self.cs(1)

    def write_data( self, data ) :
        '''Write given data to the device.  This may be
        either a single int or a bytearray of values.'''
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    # returns the display size    
    def size(self):
        return (self.width,self.height)
    
    def is_off_grid(self, xmin, ymin, xmax, ymax):
        """Check if coordinates extend past display boundaries.

        Args:
            xmin (int): Minimum horizontal pixel.
            ymin (int): Minimum vertical pixel.
            xmax (int): Maximum horizontal pixel.
            ymax (int): Maximum vertical pixel.
        Returns:
            boolean: False = Coordinates OK, True = Error.
        """
        if xmin < 0:
            print('x-coordinate: {0} below minimum of 0.'.format(xmin))
            return True
        if ymin < 0:
            print('y-coordinate: {0} below minimum of 0.'.format(ymin))
            return True
        if xmax >= self.width:
            print('x-coordinate: {0} above maximum of {1}.'.format(
                xmax, self.width - 1))
            return True
        if ymax >= self.height:
            print('y-coordinate: {0} above maximum of {1}.'.format(
                ymax, self.height - 1))
            return True
        return False
    
    def block(self, x0, y0, x1, y1, data):
        """Write a block of data to display.

        Args:
            x0 (int):  Starting X position.
            y0 (int):  Starting Y position.
            x1 (int):  Ending X position.
            y1 (int):  Ending Y position.
            data (bytes): Data buffer to write.
        """
        self._setwindowloc(x0,y0,x1,y1)
        self.write_data(data)
        
    def clear(self, color=0):
        """Clear display.

        Args:
            color (Optional int): RGB565 color value (Default: 0 = Black).
        """
        w = self.width
        h = self.height
        # Clear display in 1024 byte blocks
        if color:
            line = color.to_bytes(2, 'little') * 1024
        else:
            line = bytearray(2048)
        for x in range(0, w, 8):
            self.block(x, 0, x + 7, h - 1, line)

    def draw_image(self, path, x=0, y=0, w=128, h=128):
        """Draw image from flash.

        Args:
            path (string): Image file path.
            x (int): X coordinate of image left.  Default is 0.
            y (int): Y coordinate of image top.  Default is 0.
            w (int): Width of image.  Default is 128.
            h (int): Height of image.  Default is 128.
        """
        x2 = x + w - 1
        y2 = y + h - 1
        if self.is_off_grid(x, y, x2, y2):
            return
        with open(path, "rb") as f:
            chunk_height = 1024 // w
            chunk_count, remainder = divmod(h, chunk_height)
            chunk_size = chunk_height * w * 2
            chunk_y = y
            if chunk_count:
                for c in range(0, chunk_count):
                    buf = f.read(chunk_size)
                    self.block(x, chunk_y,
                               x2, chunk_y + chunk_height - 1,
                               buf)
                    chunk_y += chunk_height
            if remainder:
                buf = f.read(remainder * w * 2)
                self.block(x, chunk_y,
                           x2, chunk_y + remainder - 1,
                           buf)
                
    def image(self, path, x=0, y=0, w=128, h=128):
        """Draw image from flash.

        Args:
            path (string): Image file path.
            x (int): X coordinate of image left.  Default is 0.
            y (int): Y coordinate of image top.  Default is 0.
            w (int): Width of image.  Default is 128.
            h (int): Height of image.  Default is 128.
        """
        x2 = x + w - 1
        y2 = y + h - 1
        if self.is_off_grid(x, y, x2, y2):
            return
        with open(path, "rb") as f:
            self.buffer = f.read()
            
    def load_sprite(self, path, w, h):
        """Load sprite image.

        Args:
            path (string): Image file path.
            w (int): Width of image.
            h (int): Height of image.
        Notes:
            w x h cannot exceed 2048
        """
        buf_size = w * h * 2
        with open(path, "rb") as f:
            return f.read(buf_size)
        
    def draw_sprite(self, buf, x, y, w, h):
        """Draw a sprite (optimized for horizontal drawing).

        Args:
            buf (bytearray): Buffer to draw.
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of drawing.
            h (int): Height of drawing.
        """
        x2 = x + w - 1
        y2 = y + h - 1
        if self.is_off_grid(x, y, x2, y2):
            return
        self.block(x, y, x2, y2, buf)
        
    def set_rgb( self, colorRGB = True ) :
        '''True = rgb else bgr'''
        self._rgb = colorRGB
        self.setMADCTL()
        
    def setMADCTL( self ) :
        '''Set screen rotation and RGB/BGR format.'''
        self.write_cmd(self.MADCTL)
        colorcode = ST7735RGB if self._rgb else ST7735BGR
        #print("rgb: ",colorcode)
        self.write_data(bytearray([ST7735Rotations[self.rotate] | colorcode]))

    def rotation( self, rot ) :
        '''0 - 3. Starts vertical with top toward pins and rotates 90 deg
        clockwise each step.'''
        if (0 <= rot < 4):
            rotchange = self.rotate ^ rot
            self.rotate = rot
        #If switching from vertical to horizontal swap x,y
        # (indicated by bit 0 changing).
        if (rotchange & 1):
            self._size =(self.height, self.width)
        self.setMADCTL()

    def display_off(self):
        """Turn display off."""
        self.write_cmd(DISPOFF)

    def display_on(self):
        """Turn display on."""
        self.write_cmd(DISPON)

    def cleanup(self):
        """Clean up resources."""
        self.clear()
        self.display_off()
        self.spi.deinit()
        print('display off')
    
    def draw_pixel(self, x, y, color):
        """Draw a single pixel.

        Args:
            x (int): X position.
            y (int): Y position.
            color (int): RGB565 color value.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self._setwindowpoint(x,y)
            self._pushcolor(color)
        
    def draw_hline(self, x, y, w, color):
        """Draw a horizontal line.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of line.
            color (int): RGB565 color value.
        """
        start_x = clamp(x, 0, self.width)
        start_y = clamp(y, 0, self.height)
        stop_x = clamp(x + w, 0, self.width)
        #Make sure smallest x 1st.
        if (stop_x < start_x):
            start_x, stop_x = stop_x, start_x
        self._setwindowloc(start_x, start_y, stop_x, start_y)
        self._setColor(color)
        self._draw(w)
        
    def draw_vline(self, x, y, h, color):
        """Draw a vertical line.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            h (int): Height of line.
            color (int): RGB565 color value.
        """
        start_x = clamp(x, 0, self.width)
        start_y = clamp(y, 0, self.height)
        stop_y = clamp(y + h, 0, self.height)
        #Make sure smallest y 1st.
        if (stop_y < start_y):
            start_y, stop_y = stop_y, start_y
        self._setwindowloc(start_x, start_y, start_x, stop_y)
        self._setColor(color)
        self._draw(h)
        
    def draw_line(self, x1, y1, x2, y2, color):
        """Draw a line using Bresenham's algorithm.

        Args:
            x1, y1 (int): Starting coordinates of the line
            x2, y2 (int): Ending coordinates of the line
            color (int): RGB565 color value.
        """
        # Check for horizontal line
        if y1 == y2:
            if x1 > x2:
                x1, x2 = x2, x1
            self.draw_hline(x1, y1, x2 - x1 + 1, color)
            return
        # Check for vertical line
        if x1 == x2:
            if y1 > y2:
                y1, y2 = y2, y1
            self.draw_vline(x1, y1, y2 - y1 + 1, color)
            return
        
        dx = x2 - x1
        dy = y2 - y1
        inx = 1 if dx > 0 else -1
        iny = 1 if dy > 0 else -1

        dx = abs(dx)
        dy = abs(dy)
        if (dx >= dy):
            dy <<= 1
            e = dy - dx
            dx <<= 1
            while (x1 != x2):
                self.draw_pixel(x1, y1, color)
                if (e >= 0):
                    y1 += iny
                    e -= dx
                e += dy
                x1 += inx
        else:
            dx <<= 1
            e = dx - dy
            dy <<= 1
            while (y1 != y2):
                self.draw_pixel(x1, y1, color)
                if (e >= 0):
                    x1 += inx
                    e -= dy
                e += dx
                y1 += iny
        
    def draw_lines(self, coords, color):
        """Draw multiple lines.

        Args:
            coords ([[int, int],...]): Line coordinate X, Y pairs
            color (int): RGB565 color value.
        """
        # Starting point
        x1, y1 = coords[0]
        # Iterate through coordinates
        for i in range(1, len(coords)):
            x2, y2 = coords[i]
            self.draw_line(x1, y1, x2, y2, color)
            x1, y1 = x2, y2

    def lines(self, coords, color):
        # Starting point
        x1, y1 = coords[0]
        # Iterate through coordinates
        for i in range(1, len(coords)):
            x2, y2 = coords[i]
            self.line(x1, y1, x2, y2, color)
            x1, y1 = x2, y2
            
    def draw_rectangle(self, x, y, w, h, color):
        """Draw a rectangle.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of rectangle.
            h (int): Height of rectangle.
            color (int): RGB565 color value.
        """
        x2 = x + w - 1
        y2 = y + h - 1
        self.draw_hline(x, y, w, color)
        self.draw_hline(x, y2, w, color)
        self.draw_vline(x, y, h, color)
        self.draw_vline(x2, y, h, color)
        
    def draw_polygon(self, sides, x0, y0, r, color, rotate=0):
        """Draw an n-sided regular polygon.

        Args:
            sides (int): Number of polygon sides.
            x0, y0 (int): Coordinates of center point.
            r (int): Radius.
            color (int): RGB565 color value.
            rotate (Optional float): Rotation in degrees relative to origin.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the radius is integer rounded
            up to complete on a full pixel.  Therefore diameter = 2 x r + 1.
        """
        coords = []
        theta = radians(rotate)
        n = sides + 1
        for s in range(n):
            t = 2.0 * pi * s / sides + theta
            coords.append([int(r * cos(t) + x0), int(r * sin(t) + y0)])

        # Cast to python float first to fix rounding errors
        self.draw_lines(coords, color=color)

    def polygon( self, sides, x0, y0, r, color, rotate=0):
        coords = []
        theta = radians(rotate)
        n = sides + 1
        for s in range(n):
            t = 2.0 * pi * s / sides + theta
            coords.append([int(r * cos(t) + x0), int(r * sin(t) + y0)])
            
        # Cast to python float first to fix rounding errors
        self.lines(coords, color=color)
        
    def draw_circle(self, x0, y0, r, color):
        """Draw a circle.

        Args:
            x0 (int): X coordinate of center point.
            y0 (int): Y coordinate of center point.
            r (int): Radius.
            color (int): RGB565 color value.
        """
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        self.draw_pixel(x0, y0 + r, color)
        self.draw_pixel(x0, y0 - r, color)
        self.draw_pixel(x0 + r, y0, color)
        self.draw_pixel(x0 - r, y0, color)
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            self.draw_pixel(x0 + x, y0 + y, color)
            self.draw_pixel(x0 - x, y0 + y, color)
            self.draw_pixel(x0 + x, y0 - y, color)
            self.draw_pixel(x0 - x, y0 - y, color)
            self.draw_pixel(x0 + y, y0 + x, color)
            self.draw_pixel(x0 - y, y0 + x, color)
            self.draw_pixel(x0 + y, y0 - x, color)
            self.draw_pixel(x0 - y, y0 - x, color)

    def circle(self, x0, y0, r, color):
        """Draw a circle.

        Args:
            x0 (int): X coordinate of center point.
            y0 (int): Y coordinate of center point.
            r (int): Radius.
            color (int): RGB565 color value.
        """
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        self.pixel(x0, y0 + r, color)
        self.pixel(x0, y0 - r, color)
        self.pixel(x0 + r, y0, color)
        self.pixel(x0 - r, y0, color)
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            self.pixel(x0 + x, y0 + y, color)
            self.pixel(x0 - x, y0 + y, color)
            self.pixel(x0 + x, y0 - y, color)
            self.pixel(x0 - x, y0 - y, color)
            self.pixel(x0 + y, y0 + x, color)
            self.pixel(x0 - y, y0 + x, color)
            self.pixel(x0 + y, y0 - x, color)
            self.pixel(x0 - y, y0 - x, color)
       
            
    def draw_ellipse(self, x0, y0, a, b, color):
        """Draw an ellipse.

        Args:
            x0, y0 (int): Coordinates of center point.
            a (int): Semi axis horizontal.
            b (int): Semi axis vertical.
            color (int): RGB565 color value.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the axes are integer rounded
            up to complete on a full pixel.  Therefore the major and
            minor axes are increased by 1.
        """
        a2 = a * a
        b2 = b * b
        twoa2 = a2 + a2
        twob2 = b2 + b2
        x = 0
        y = b
        px = 0
        py = twoa2 * y
        # Plot initial points
        self.draw_pixel(x0 + x, y0 + y, color)
        self.draw_pixel(x0 - x, y0 + y, color)
        self.draw_pixel(x0 + x, y0 - y, color)
        self.draw_pixel(x0 - x, y0 - y, color)
        # Region 1
        p = round(b2 - (a2 * b) + (0.25 * a2))
        while px < py:
            x += 1
            px += twob2
            if p < 0:
                p += b2 + px
            else:
                y -= 1
                py -= twoa2
                p += b2 + px - py
            self.draw_pixel(x0 + x, y0 + y, color)
            self.draw_pixel(x0 - x, y0 + y, color)
            self.draw_pixel(x0 + x, y0 - y, color)
            self.draw_pixel(x0 - x, y0 - y, color)
        # Region 2
        p = round(b2 * (x + 0.5) * (x + 0.5) +
                  a2 * (y - 1) * (y - 1) - a2 * b2)
        while y > 0:
            y -= 1
            py -= twoa2
            if p > 0:
                p += a2 - py
            else:
                x += 1
                px += twob2
                p += a2 - py + px
            self.draw_pixel(x0 + x, y0 + y, color)
            self.draw_pixel(x0 - x, y0 + y, color)
            self.draw_pixel(x0 + x, y0 - y, color)
            self.draw_pixel(x0 - x, y0 - y, color)
 
    def draw_filledCircle(self, x0, y0, r, color):
        """Draw a filled circle.

        Args:
            x0 (int): X coordinate of center point.
            y0 (int): Y coordinate of center point.
            r (int): Radius.
            color (int): RGB565 color value.
        """
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        self.draw_vline(x0, y0 - r, 2 * r + 1, color)
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            self.draw_vline(x0 + x, y0 - y, 2 * y + 1, color)
            self.draw_vline(x0 - x, y0 - y, 2 * y + 1, color)
            self.draw_vline(x0 - y, y0 - x, 2 * x + 1, color)
            self.draw_vline(x0 + y, y0 - x, 2 * x + 1, color)
            
    def fill_circle(self, x0, y0, r, color):
        """Draw a filled circle.

        Args:
            x0 (int): X coordinate of center point.
            y0 (int): Y coordinate of center point.
            r (int): Radius.
            color (int): RGB565 color value.
        """
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        self.vline(x0, y0 - r, 2 * r + 1, color)
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            self.vline(x0 + x, y0 - y, 2 * y + 1, color)
            self.vline(x0 - x, y0 - y, 2 * y + 1, color)
            self.vline(x0 - y, y0 - x, 2 * x + 1, color)
            self.vline(x0 + y, y0 - x, 2 * x + 1, color)
            
    def draw_filledEllipse(self, x0, y0, a, b, color):
        """Draw a filled ellipse.

        Args:
            x0, y0 (int): Coordinates of center point.
            a (int): Semi axis horizontal.
            b (int): Semi axis vertical.
            color (int): RGB565 color value.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the axes are integer rounded
            up to complete on a full pixel.  Therefore the major and
            minor axes are increased by 1.
        """
        a2 = a * a
        b2 = b * b
        twoa2 = a2 + a2
        twob2 = b2 + b2
        x = 0
        y = b
        px = 0
        py = twoa2 * y
        # Plot initial points
        self.draw_line(x0, y0 - y, x0, y0 + y, color)
        # Region 1
        p = round(b2 - (a2 * b) + (0.25 * a2))
        while px < py:
            x += 1
            px += twob2
            if p < 0:
                p += b2 + px
            else:
                y -= 1
                py -= twoa2
                p += b2 + px - py
            self.draw_line(x0 + x, y0 - y, x0 + x, y0 + y, color)
            self.draw_line(x0 - x, y0 - y, x0 - x, y0 + y, color)
        # Region 2
        p = round(b2 * (x + 0.5) * (x + 0.5) +
                  a2 * (y - 1) * (y - 1) - a2 * b2)
        while y > 0:
            y -= 1
            py -= twoa2
            if p > 0:
                p += a2 - py
            else:
                x += 1
                px += twob2
                p += a2 - py + px
            self.draw_line(x0 + x, y0 - y, x0 + x, y0 + y, color)
            self.draw_line(x0 - x, y0 - y, x0 - x, y0 + y, color)
            
    def fill_ellipse(self, x0, y0, a, b, color):
        """Draw a filled ellipse.

        Args:
            x0, y0 (int): Coordinates of center point.
            a (int): Semi axis horizontal.
            b (int): Semi axis vertical.
            color (int): RGB565 color value.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the axes are integer rounded
            up to complete on a full pixel.  Therefore the major and
            minor axes are increased by 1.
        """
        a2 = a * a
        b2 = b * b
        twoa2 = a2 + a2
        twob2 = b2 + b2
        x = 0
        y = b
        px = 0
        py = twoa2 * y
        # Plot initial points
        self.line(x0, y0 - y, x0, y0 + y, color)
        # Region 1
        p = round(b2 - (a2 * b) + (0.25 * a2))
        while px < py:
            x += 1
            px += twob2
            if p < 0:
                p += b2 + px
            else:
                y -= 1
                py -= twoa2
                p += b2 + px - py
            self.line(x0 + x, y0 - y, x0 + x, y0 + y, color)
            self.line(x0 - x, y0 - y, x0 - x, y0 + y, color)
        # Region 2
        p = round(b2 * (x + 0.5) * (x + 0.5) +
                  a2 * (y - 1) * (y - 1) - a2 * b2)
        while y > 0:
            y -= 1
            py -= twoa2
            if p > 0:
                p += a2 - py
            else:
                x += 1
                px += twob2
                p += a2 - py + px
            self.line(x0 + x, y0 - y, x0 + x, y0 + y, color)
            self.line(x0 - x, y0 - y, x0 - x, y0 + y, color)

    def draw_filledRectangle(self, x, y, w, h, color):
        """Draw a filled rectangle.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of rectangle.
            h (int): Height of rectangle.
            color (int): RGB565 color value.
        """
        start_x = clamp(x, 0, self.width)
        start_y = clamp(y, 0, self.height)
        end_x   = clamp(start_x + w - 1, 0, self.width)
        end_y   = clamp(y + h - 1, 0, self.height)

        if (end_x < start_x):
            tmp = end_x
            end_x = start_x
            start_x = tmp
            
        if (end_y < start_y):
            tmp = end_y
            end = (end[0], start[1])
            start_y = tmp

        self._setwindowloc(start_x,start_y,end_x,end_y)
        numPixels = (end_x - start_x + 1) * (end_y - start_y + 1)
        # print("color: {:04x}".format(color))
        self._setColor(color)
        self._draw(numPixels)


    def draw_filledPolygon(self, sides, x0, y0, r, color, rotate=0):
        """Draw a filled n-sided regular polygon.

        Args:
            sides (int): Number of polygon sides.
            x0, y0 (int): Coordinates of center point.
            r (int): Radius.
            color (int): RGB565 color value.
            rotate (Optional float): Rotation in degrees relative to origin.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the radius is integer rounded
            up to complete on a full pixel.  Therefore diameter = 2 x r + 1.
        """
        # Determine side coordinates
        coords = []
        theta = radians(rotate)
        n = sides + 1
        for s in range(n):
            t = 2.0 * pi * s / sides + theta
            coords.append([int(r * cos(t) + x0), int(r * sin(t) + y0)])
        # Starting point
        x1, y1 = coords[0]
        # Minimum Maximum X dict
        xdict = {y1: [x1, x1]}
        # Iterate through coordinates
        for row in coords[1:]:
            x2, y2 = row
            xprev, yprev = x2, y2
            # Calculate perimeter
            # Check for horizontal side
            if y1 == y2:
                if x1 > x2:
                    x1, x2 = x2, x1
                if y1 in xdict:
                    xdict[y1] = [min(x1, xdict[y1][0]), max(x2, xdict[y1][1])]
                else:
                    xdict[y1] = [x1, x2]
                x1, y1 = xprev, yprev
                continue
            # Non horizontal side
            # Changes in x, y
            dx = x2 - x1
            dy = y2 - y1
            # Determine how steep the line is
            is_steep = abs(dy) > abs(dx)
            # Rotate line
            if is_steep:
                x1, y1 = y1, x1
                x2, y2 = y2, x2
            # Swap start and end points if necessary
            if x1 > x2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            # Recalculate differentials
            dx = x2 - x1
            dy = y2 - y1
            # Calculate error
            error = dx >> 1
            ystep = 1 if y1 < y2 else -1
            y = y1
            # Calculate minimum and maximum x values
            for x in range(x1, x2 + 1):
                if is_steep:
                    if x in xdict:
                        xdict[x] = [min(y, xdict[x][0]), max(y, xdict[x][1])]
                    else:
                        xdict[x] = [y, y]
                else:
                    if y in xdict:
                        xdict[y] = [min(x, xdict[y][0]), max(x, xdict[y][1])]
                    else:
                        xdict[y] = [x, x]
                error -= abs(dy)
                if error < 0:
                    y += ystep
                    error += dx
            x1, y1 = xprev, yprev
        # Fill polygon
        for y, x in xdict.items():
            self.draw_hline(x[0], y, x[1] - x[0] + 2, color)

    def _getletter(self,letter,font,color,background,landscape):
        '''
        gets a letter from the font and fills the letter array with the pixel colors
        returns the filled letter array ready to be printed as well as width and height
        of the array.
        Depending on the landscape parameter the letter may be rotated
        '''
        pixels, width, height = font.get_ch(letter)
        if font.hmap():
            #print("hmap true: exchanging width and height")
            width,height = height,width
            
        #print("width: {:d}, height: {:d}, no of bytes in pixel array: {:d}".format(width,height,len(pixels)))
        #print("Color: foreground: {:04x}, background: {:04x}".format(color,background))
        bytes_per_row = (width-1)//8 +1
        #print("bytes_per_row: ",bytes_per_row)

        """
        for i in range(height):
            ch = pixels[bytes_per_row*i]
            for j in range(bytes_per_row-1):
                ch |= pixels[2*i+j+1] << 8*(j+1)
            print("{:04x}".format(ch))
            #print(hex(pixels[2*i])," ",hex(pixels[2*i+1]),end=" ")
            #print(hex(row)," ",end="")
        print("")
        """
        #
        # print the letter in its original form
        #
        #print("Fill the color:\n")
        letter = bytearray(background.to_bytes(2, 'little') * width * height) # color needs 2 bytes
        for i in range(height):
            if font.hmap():
                mask = 0x80 << (bytes_per_row-1)*8
                #print("font.hmap")
                ch = pixels[bytes_per_row*i] << 8*(bytes_per_row-1)
                for j in range(bytes_per_row-1):
                    ch |= pixels[bytes_per_row*i+j+1]
            else:
                mask = 1 << (width-1)
                ch = pixels[bytes_per_row*i]
                for j in range(bytes_per_row-1):
                    ch |= pixels[bytes_per_row*i+j+1] << 8*(j+1)

            if font.hmap():
                for k in range(width):
                    if landscape:
                        if mask & ch:
                            letter[2*(height*(width-1)-k*height+i)] = color & 0xff
                            letter[2*(height*(width-1)-k*height+i)+1] = (color >> 8) & 0xff
                        #    print('x ',end="")
                        #else:
                        #    print('. ',end="")
                    else:
                        if mask & ch:
                            letter[2*(i*width+k)] = color & 0xff
                            letter[2*(i*width+k)+1] = (color >> 8) & 0xff
                        #    print('x ',end="")
                        #else:
                        #    print('. ',end="")
                    mask >>=1
            else:
                for k in range(width):
                    if landscape:
                        if mask & ch:
                            letter[2*(height*width-1-(i*width+k))]=  color & 0xff
                            letter[2*(height*width-1-(i*width+k))+1]=(color>>8) & 0xff
                        #    print('x ',end="")
                        #else:
                        #    print('. ',end="")
                    else:
                        if mask & ch:
                            letter[2*((width-k-1)*height+i)]  = color & 0xff
                            letter[2*((width-k-1)*height+i)+1]= (color >> 8) & 0xff
                        #    print('x ',end="")
                        #else:
                        #    print('. ',end="")
                    mask >>=1
            #print("")
            
        #print("\nfilled glyph:\n")
        """
        if font.hmap():
            if landscape:
                print("landscape")
                # in landscape mode width and height are inverted                   
                w,h = height,width
            else:
                print("portrait")
                w,h = width,height
            for i in range(h):
                for j in range(w):
                    color = letter[2*(i*w+j)] | (letter[2*(i*w+j)+1] << 2)
                    if color:
                        print('x ',end="")
                    else:
                        print('. ',end="")
                print("")
        else:
            if landscape:
                print("landscape")
                # in landscape mode width and height are inverted                   
                w,h = height,width
            else:
                print("portrait")
                w,h = width,height
            for i in range(w):
                for j in range(h):
                    color = letter[2*(i*h+j)] | (letter[2*(i*h+j)+1] << 2)
                    if color:
                        print('x ',end="")
                    else:
                        print('. ',end="")
                print("")
        """
        if font.hmap():
            if landscape:
                return letter,height,width
            else:
                return letter,width,height
        else:
            if landscape:
                return letter,width,height
            else:
                return letter,height,width
    
    def draw_letter(self, x, y, letter, font, color, background=0,
                    landscape=False):

        letter, width,height = self._getletter(letter,font,color,background,landscape)      
        #print("draw_letter: width: {:d} height: {:d}".format(width,height))

        if landscape:
            self.block(x,y-height,x+width-1,y,letter)
        else:
            self.block(x,y,x+width-1,y+height-1,letter)
            
    def letter(self, x, y, letter, color, font=sysfont, background=0,
                    landscape=False):
        letter, width,height = self._getletter(letter,font,color,background,landscape)      
        #print("draw_letter: width: {:d} height: {:d}".format(width,height))
        # copy to frame buffer
        if landscape:
            print("width: {:d}, height: {:.d}".format(width,height))
            for i in range(width):
                print("buf[{:03d} .. {:03d}] from letter[{:03d} .. {:03d}]".format(2*((y+i)*self.width+x),2*((y+i)*self.width+x+width),2*i*width,2*(i*width+width)))
                self.buffer[2*((y-height+i)*self.width+x): 2*((y-height+i)*self.width+x+width)] = letter[2*i*width:2*(i*width+width)]                          
        else:
            print("width: {:d}, height: {:.d}".format(width,height))
            for i in range(height):
                print("buf[{:03d} .. {:03d}] from letter[{:03d} .. {:03d}]".format(2*((y+i)*self.width+x),2*((y+i)*self.width+x+width),2*i*width,2*(i*width+width)))
                self.buffer[2*((y+i)*self.width+x): 2*((y+i)*self.width+x+width)] = letter[2*i*width:2*(i*width+width)]
               
    def draw_text(self, x, y, text, font, color,  background=0,
                  landscape=False, spacing=1, nowrap = False):
        """Draw text.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            text (string): Text to draw.
            font (XglcdFont object): Font.
            color (int): RGB565 color value.
            background (int): RGB565 background color (default: black).
            landscape (bool): Orientation (default: False = portrait)
            spacing (int): Pixels between letters (default: 1)
        """
        for letter in text:
            
            # Get letter array and letter dimensions
            glyph, w, h = self._getletter(letter, font, color, background,
                                    landscape)
            # Stop on error
            if w == 0 or h == 0:
                print('Invalid width {0} or height {1}'.format(w, h))
                return
            # draw the letter
            
            if landscape:
                self.block(x,y-h,x+w-1,y,glyph)
                # Fill in spacing
                if spacing:
                    self.draw_filledRectangle(x, y - h - spacing, w, spacing, background)
                # Position y for next letter
                y -= (h + spacing)
                #print("{:d} ".format(y),end="")
                if y -w < 0:
                    if nowrap:
                        break;
                    else:
                        y=127
                        x += w
                        # print("x: ",x)
                        if x+w > self.width:
                            break                
            else:
                # Fill in spacing
                self.block(x,y,x+w-1,y+h-1,glyph)
                if spacing:
                    self.draw_filledRectangle(x + w, y, spacing, h, background)
                # Position x for next letter
                x += w + spacing
                #print("{:d} ".format(x),end="")
                if x + w > self.width:
                    if nowrap:
                        break;
                    else:
                        x=0
                        y += h
                        # print("y: ",y)
                        if y + h > self.height:
                            break
            #print("")
    # method used be ssd1306 test

    def text(self, x, y, text, color, font=sysfont,  background=0,
                  landscape=False, spacing=1, nowrap = False):
        """Draw text to frame buffer.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            text (string): Text to draw.
            font (XglcdFont object): Font.
            color (int): RGB565 color value.
            background (int): RGB565 background color (default: black).
            landscape (bool): Orientation (default: False = portrait)
            spacing (int): Pixels between letters (default: 1)
        """
        for letter in text:
            # Get letter array and letter dimensions
            glyph, w, h = self._getletter(letter, font, color, background,
                                    landscape)
            # Stop on error
            if w == 0 or h == 0:
                print('Invalid width {0} or height {1}'.format(w, h))
                return
            # write the letter to the framebuffer
                    # copy to frame buffer
                    
            if landscape:
                #print("width: {:d}, height: {:.d}".format(w,h))
                for i in range(h):
                    #print("buf[{:03d} .. {:03d}] from letter[{:03d} .. {:03d}]".format(2*((y-h+i)*self.width+x),2*((y-h+i)*self.width+x+w),2*i*w,2*(i*w+w)))
                    self.buffer[2*((y-h+i)*self.width+x): 2*((y-h+i)*self.width+x+w)] = glyph[2*i*w:2*(i*w+w)]      
                # Fill in spacing
                if spacing:
                    self.fill_rect(x, y - h - spacing, w, spacing, background)
                # Position y for next letter
                # print("x,y: {:d},{:d} height: {:d}".format(x,y,h))
                y -= (h + spacing)
                if y -h < 0:
                    if nowrap:
                        break;
                    else:
                        y=127
                        x += w
                        # print("x: ",x)
                        if x+w > self.width:
                            break                
            else:
                # portrait mode
                # print("width: {:d}, height: {:.d}".format(w,h))
                for i in range(h):
                    #print("buf[{:03d} .. {:03d}] from letter[{:03d} .. {:03d}]".format(2*((y+i)*self.width+x),2*((y+i)*self.width+x+w),2*i*w,2*(i*w+w)))
                    self.buffer[2*((y+i)*self.width+x): 2*((y+i)*self.width+x+w)] = glyph[2*i*w:2*(i*w+w)]
                # Fill in spacing
                if spacing:
                    self.fill_rect(x + w, y, spacing, h, background)
                # Position x for next letter
                x += w + spacing
                if x + w > self.width:
                    if nowrap:
                        break;
                    else:
                        x=0
                        y += h
                        # print("y: ",y)
                        if y + h > self.height:
                            break


    #def show(self):
    #    buf = bytearray(2*self.width)
    #    for i in range(self.height):
    #        for j in range(self.width):
    #            buf[2*j] = self.buffer[2*i*self.width+2*j+1]
    #            buf[2*j+1] = self.buffer[2*i*self.width+2*j]         # swap the color bytes
    #        self._setwindowloc(0,i,self.width,i) # the ith line
    #        self.write_data(buf)
    #    return

    def show(self):
        row=bytearray(2*self.width)
        for i in range(self.height):
            self._setwindowloc(0,i,self.width,i) # the ith line
            self.write_data(self.buffer[2*i*self.width : 2*i*self.width+2*self.width])
        return
    

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

'''
oled = Display(spi,SPI_CS,SPI_DC)
print("Green: {:04x}".format(Display.GREEN))
oled.clear()
oled.draw_text(0,0,'Hello World!',courier20,Display.GREEN)
time.sleep(2)
oled.clear()
oled.draw_text(0,127,'Hello World!',courier20,Display.GREEN,landscape=True)
time.sleep(2)
oled.clear()
#oled.draw_letter(0,127,'H',courier20,Display.GREEN,landscape=True)
#oled.letter(0,0,'H',Display.GREEN,font=courier20)
#oled.letter(0,127,'H',Display.GREEN,font=courier20,landscape=True)
oled.text(0,0,'Hello World!',Display.YELLOW,font=courier20)
oled.show()
oled.fill(Display.BLACK)
time.sleep(2)
oled.text(0,127,'Hello World!',Display.YELLOW,font=courier20,landscape=True)
oled.show()
#oled.draw_letter(50,70,'F',sysfont,Display.GREEN)
#oled.draw_letter(60,70,'F',sysfont,Display.GREEN,landscape=True)
time.sleep(3)
#oled.clear()
oled.text(0,0,'Hello World!',courier20,Display.YELLOW)
oled.show()
#oled._getletter('F',sysfont,Display.GREEN,landscape=True)
#oled._getletter('F',courier20,Display.GREEN,landscape=True)

print("Rectangle in hardware")
oled.draw_filledRectangle(50,50,50,50,Display.GREEN)
time.sleep(5)
oled.clear()
time.sleep(2)
print("Rectangle in frame buffer")
oled.fill_rect(50,50,50,50,Display.GREEN)
oled.show()
time.sleep(5)

'''
