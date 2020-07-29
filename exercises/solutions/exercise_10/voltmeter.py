from machine import Pin,SPI,ADC
import gc,sys
from ST7735 import Display,color565
import cmath
from nanogui import DObject, Label, Pointer, polar, conj, refresh

# Fonts
import fonts.arial10 as arial10
from writer import Writer, CWriter
import utime
import uos

sck = Pin(18)
miso= Pin(19)
mosi= Pin(23)
SPI_CS = 26
SPI_DC = 5
spi = SPI(2, baudrate=32000000, sck=sck, mosi=mosi, miso=miso)
ADC_PIN = 34

st7735 =Display(spi,SPI_CS,SPI_DC)
adc = ADC(Pin(ADC_PIN))  # create ADC object on ADC pin 34
adc.atten(ADC.ATTN_11DB) # This gives us max value at ~ 3.3V

refresh(st7735)
GREEN = color565(0, 255, 0)
RED = color565(255, 0, 0)
BLUE = color565(0, 0, 255)
YELLOW = color565(255, 255, 0)
BLACK = 0

CWriter.set_textpos(st7735, 0, 0)  # In case previous tests have altered it
wri = CWriter(st7735, arial10, GREEN, BLACK, verbose=False)
wri.set_clip(True, True, False)
    
# Draw an arrow; origin and vec are complex, scalar lc defines length of chevron.
# cw and ccw are unit vectors of +-3pi/4 radians for chevrons (precompiled)
def needle(dev, origin, vec, lc, color, ccw=cmath.exp(3j * cmath.pi/4), cw=cmath.exp(-3j * cmath.pi/4)):
    length, theta = cmath.polar(vec)
    uv = cmath.rect(1, theta)  # Unit rotation vector
    start = -vec
    if length > 3 * lc:  # If line is long
        ds = cmath.rect(lc, theta)
        start += ds  # shorten to allow for length of tail chevrons
    chev = lc + 0j
    polar(dev, origin, vec, color)  # Origin to tip
    polar(dev, origin + conj(vec), chev*ccw*uv, color)  # Tip chevron
    polar(dev, origin + conj(vec), chev*cw*uv, color)

def _halfcircle(dev, x0, y0, r, color): # Single pixel circle
    x = -r
    y = 0
    err = 2 -2*r
    while x <= 0:
        #dev.pixel(x0 -x, y0 +y, color)
        #dev.pixel(x0 +x, y0 +y, color)
        dev.pixel(x0 +x, y0 -y, color)
        dev.pixel(x0 -x, y0 -y, color)
        e2 = err
        if (e2 <= y):
            y += 1
            err += y*2 +1
            if (-x == y and e2 <= x):
                e2 = 0
        if (e2 > x):
            x += 1
            err += x*2 +1

def halfcircle(dev, x0, y0, r, color, width =1): # Draw circle
    x0, y0, r = int(x0), int(y0), int(r)
    for r in range(r, r -width, -1):
        _halfcircle(dev, x0, y0, r, color)

    dev.hline(x0-r, y0, 2*r, color)
    
#halfcircle(st7735,64,64,63,Display.GREEN)

class Scale(DObject):

    def __init__(self, writer, row, col, *, height=50,
                 fgcolor=None, bgcolor=None, bdcolor=False, ticks=8,
                 label=None, style=0, pip=None):
        super().__init__(writer, row, col, height, 2*height, fgcolor, bgcolor, bdcolor)
        self.style = style
        self.pip = self.fgcolor if pip is None else pip
        if label is not None:
            self.label = Label(writer, row + height + 20, col, label)
        self.minLabel = Label(writer, row + height + 5, col, '0.0V')
        self.minLabel = Label(writer, row + height + 5, col+2*height-25, '5.0V')        
        radius = height
        self.radius = radius
        self.ticks = ticks
        self.xorigin = col + radius
        self.yorigin = row + radius
        self.vectors = set()
        
    def show(self):
        super().show()
        # cache bound variables
        dev = self.device
        ticks = self.ticks
        radius = self.radius
        xo = self.xorigin
        yo = self.yorigin
        # vectors (complex)
        vor = xo + 1j * yo
        vtstart = 0.9 * radius + 0j  # start of tick
        vtick = 0.1 * radius + 0j  # tick
        vrot = cmath.exp(2j * cmath.pi/(2*ticks))  # unit rotation
        for _ in range(ticks):
            polar(dev, vor + conj(vtstart), vtick, self.fgcolor)
            vtick *= vrot
            vtstart *= vrot
        halfcircle(dev, xo, yo, radius, self.fgcolor)
        vshort = 1000  # Length of shortest vector
        for v in self.vectors:
            color = self.fgcolor if v.color is None else v.color
            val = v.value() * radius  # val is complex
            vshort = min(vshort, cmath.polar(val)[0])
            needle(dev, vor, val, 5, color)
#            if self.style == Scale.CLOCK:
#                polar(dev, vor, val, color)
#            else:
#                arrow(dev, vor, val, 5, color)

def voltmeter():
    print('Voltmeter with ADC connected to pin 34')
    refresh(st7735, True)  # Clear any prior imag
    title = Label(wri, 2, 40, 'Voltmeter', fgcolor=Display.WHITE, bdcolor=Display.WHITE)    
    uv = lambda phi : cmath.rect(1, phi)  # Return a unit vector of phase phi

    scale =  Scale(wri, 30, 5, height = 60, ticks = 5, bdcolor=None, label=50)  # Border in fg color
    voltage = Pointer(scale)

    while True:
        v= adc.read() * 3.3 /4096   # we have Vdd = 3.3 V and a 12 bit ADC
        voltage.value((0 + 0.9j)*cmath.rect(1, cmath.pi/2 - (v/5)*cmath.pi),Display.RED)
        scale.text('voltage: {0:.1f} V'.format(v))
        refresh(st7735)
        utime.sleep_ms(100)   # a measurement everv 100 ms
#    for n in range(31):
#        refresh(st7735)
#        utime.sleep_ms(200)

#        voltage.value(voltage.value() * dm, Display.RED)

voltmeter()
utime.sleep(10)
