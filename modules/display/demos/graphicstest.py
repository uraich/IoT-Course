from ST7735 import Display
import fonts.sysfont as sysfont
from machine import SPI,Pin
import time
import math
import sys

if sys.platform == 'esp8266':
    print('1.4 inch TFT screen test on ESP8266')
    SPI_CS = 16
    SPI_DC = 15
    spi = SPI(1)
    tft=Display(spi,SPI_DC,SPI_CS)
    
elif sys.platform == 'esp32':
    print('1.4 inch TFT screen test on ESP32')
    sck = Pin(18)
    miso= Pin(19)
    mosi= Pin(23)
    SPI_CS = 26
    SPI_DC = 5
    spi = SPI(2, baudrate=32000000, sck=sck, mosi=mosi, miso=miso)
    tft=Display(spi,SPI_DC,SPI_CS)

def testlines(color):
    print("Test lines")
    tft.clear()
    for x in range(0, tft.size()[0], 6):
        tft.draw_line(0,0,x, tft.size()[1] - 1, color)
    for y in range(0, tft.size()[1], 6):
        tft.draw_line(0,0,tft.size()[0] - 1, y, color)

    tft.clear()
    for x in range(0, tft.size()[0], 6):
        tft.draw_line(tft.size()[0] - 1, 0, x, tft.size()[1] - 1, color)
    for y in range(0, tft.size()[1], 6):
        tft.line(tft.size()[0] - 1, 0, 0, y, color)
        
    tft.clear()
    for x in range(0, tft.size()[0], 6):
        tft.draw_line(0, tft.size()[1] - 1, x, 0, color)
    for y in range(0, tft.size()[1], 6):
        tft.draw_line(0, tft.size()[1] - 1, tft.size()[0] - 1,y, color)

    tft.clear()
    for x in range(0, tft.size()[0], 6):
        tft.draw_line(tft.size()[0] - 1, tft.size()[1] - 1, x, 0, color)
    for y in range(0, tft.size()[1], 6):
        tft.line(tft.size()[0] - 1, tft.size()[1] - 1, 0, y, color)
        
def testfastlines(color1, color2):
    print("Test horizontal and vertical fast lines") 
    tft.clear()
    for y in range(0, tft.size()[1], 5):
        tft.draw_hline(0, y, tft.size()[0], color1)
    for x in range(0, tft.size()[0], 5):
        tft.draw_vline(x,0, tft.size()[1], color2)
        
def testdrawrects(color):
    print("Test rectangles")         
    tft.clear()
    for x in range(0,tft.size()[0],6):
        tft.draw_rectangle(tft.size()[0]//2 - x//2, tft.size()[1]//2 - x//2, x, x, color)
        
def testfillrects(color1, color2):
    print("Test filled rectangles")     
    tft.clear()
    for x in range(tft.size()[0],0,-6):
        tft.draw_filledRectangle(tft.size()[0]//2 - x//2, tft.size()[1]//2 - x//2, x, x, color1)
        tft.draw_rectangle(tft.size()[0]//2 - x//2, tft.size()[1]//2 - x//2, x, x, color2)

def testfillcircles(radius, color):
    print("Test filled circles")
    tft.clear()
    for x in range(radius, tft.size()[0], radius * 2):
        for y in range(radius, tft.size()[1], radius * 2):
            tft.draw_filledCircle(x, y , radius, color)
        
def testdrawcircles(radius, color):
    print("Test circles")
    for x in range(0, tft.size()[0] + radius, radius * 2):
        for y in range(0, tft.size()[1] + radius, radius * 2):
            tft.draw_circle(x, y, radius, color)
        tft.show()
            
def testtriangles():
    print("Test triangles")
    tft.fill(Display.BLACK);
    color = 0xF800
    w = tft.size()[0] // 2
    x = tft.size()[1] - 1
    y = 0
    z = tft.size()[0]
    for t in range(0, 15):
        tft.draw_line(w, y, y, x, color)
        tft.draw_line(y, x, z, x, color)
        tft.draw_line(z, x, w, y, color)
        x -= 4
        y += 4
        z -= 4
        color += 100
        tft.show()
        
def testroundrects():
    print("Test differently colored rectangles")
    tft.fill(Display.BLACK);
    color = 100
    for t in range(5):
        x = 0
        y = 0
        w = tft.size()[0] - 2
        h = tft.size()[1] - 2
        for i in range(17):
            tft.draw_rectangle(x, y, w, h, color)
            x += 2
            y += 3
            w -= 4
            h -= 6
            color += 1100
        color += 100

def tftprinttest():
    tft.clear()
    print("Test text printing")
    v = 0
    tft.draw_text(0, v, "Hello World!", sysfont, Display.RED)
    v += sysfont.height()
    tft.draw_text(0, v, str(math.pi), sysfont, Display.GREEN)
    v += sysfont.height()
    tft.draw_text(0, v, " Want pi?", sysfont, Display.GREEN)
    v += sysfont.height() * 2
    tft.draw_text(0, v, hex(8675309), sysfont, Display.GREEN)
    v += sysfont.height()
    tft.draw_text(0, v, " Print HEX!", sysfont, Display.GREEN)
    v += sysfont.height() * 2
    tft.draw_text(0, v, "Sketch has been", sysfont, Display.WHITE)
    v += sysfont.height()
    tft.draw_text(0, v, "running for: ", sysfont, Display.WHITE)
    v += sysfont.height()
    tft.draw_text(0, v, str(time.ticks_ms() / 1000), sysfont, Display.CYAN)
    v += sysfont.height()
    tft.draw_text(0, v, " seconds.", sysfont, Display.WHITE)

def tfttesttextwrap():
    tft.clear()
    print("Test text wrapping")
    tft.draw_text(0, 0, "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur adipiscing ante sed nibh tincidunt feugiat. Maecenas enim massa, fringilla sed malesuada et, malesuada sit amet turpis. Sed porttitor neque ut ante pretium vitae malesuada nunc bibendum. Nullam aliquet ultrices massa eu hendrerit. Ut sed nisi lorem. In vestibulum purus a tortor imperdiet posuere. ", sysfont, Display.GREEN)
    time.sleep(5)
    tft.clear()
    tft.draw_text(0,127, "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur adipiscing ante sed nibh tincidunt feugiat. Maecenas enim massa, fringilla sed malesuada et, malesuada sit amet turpis. Sed porttitor neque ut ante pretium vitae malesuada nunc bibendum. Nullam aliquet ultrices massa eu hendrerit. Ut sed nisi lorem. In vestibulum purus a tortor imperdiet posuere. ", sysfont, Display.WHITE,landscape=True)
    time.sleep(5)
    
tft=Display(spi,SPI_CS,SPI_DC)
def test_main():

    tfttesttextwrap()
    time.sleep(5)
    
    tftprinttest()
    time.sleep(5)

    testlines(Display.YELLOW)
    time.sleep(5)

    testfastlines(Display.RED, Display.BLUE)
    time.sleep(5)

    testdrawrects(Display.GREEN)
    time.sleep(5)

    testfillrects(Display.YELLOW, Display.PURPLE)
    time.sleep(5)

    tft.fill(Display.BLACK)
    testfillcircles(10, Display.BLUE)
    testdrawcircles(10, Display.WHITE)
    time.sleep(5)

    testroundrects()
    time.sleep(5)

    testtriangles()
    time.sleep(5)

test_main()
