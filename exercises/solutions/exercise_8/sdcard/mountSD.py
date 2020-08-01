# mountSD: mounts the SD cards, create the data directory, 
# write a file with "Hello World!" and reads it back

import sys,uos,errno
import sdcard, machine

if sys.platform == 'esp8266':
    print('SD-card test on ESP8266')
    SPI_CS = 15
    spi = machine.SPI(1)

elif sys.platform == 'esp32':
    print('SD-card test on ESP32')
    sck = machine.Pin(18)
    miso= machine.Pin(19)
    mosi= machine.Pin(23)
    SPI_CS = 5
    spi = machine.SPI(2, baudrate=32000000, sck=sck, mosi=mosi, miso=miso)

sdcardAvail=True
spi.init()  # Ensure right baudrate   
try:
    sd = sdcard.SDCard(spi, machine.Pin(SPI_CS)) # ESP8266 version
except:
    sdcardAvail = False
    
if sdcardAvail:
    print("sdcard created")
else:
    print("No sdcard found")
    sys.exit(-1)

vfs = uos.VfsFat(sd)

try:
    uos.mount(vfs, '/sd')
except OSError as e:
    if len(e.args) > 0 and e.args[0] == errno.EPERM:
        print('Already mounted, skipping')
        pass
    else:
        print('problem mounting the sd card')
        sys.exit(-1)

print("SD card successfully mounted")

# check to see if /sd/data already exists
try:
    uos.stat("/sd/data")
    print("/sd/data already exists, nothing to do")
    
except OSError as e:
    if len(e.args) > 0 and e.args[0] == errno.ENOENT:
        print("/sd/data does not exist, creating it")
        uos.mkdir("/sd/data")
        
# write hello.txt file to sd card

print("Creating and writing the hello world file")
f = open("/sd/data/hello.txt","w")
f.write("Hello World!\n")
f.close()

try:
    f=open("/sd/data/hello.txt","r")
    text=f.read()
    print("Read from /sd/data/hello.txt: ",text,end="")
    f.close()

except:
    print("Failed to open /sd/data/hello.txt")
    
