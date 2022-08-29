#
# cayenneWS2812B.py
# The WS2812B is an rgb LED whose color components can be controlled through
# sliders in Cayenne. The program registers a command callback and, dependant
# on the channel employed, sets the corresponding color component
# 
# copyright U. Raich
# This is a demo program for the workshop on IoT at the African Internet Summit 2019
# Released under GPL
#
from machine import Pin
import neopixel
import cayenne.client
import time,sys
import ulogging as logging

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "your mqtt user code"
MQTT_PASSWORD  = "your mqtt password"
MQTT_CLIENT_ID = "your mqtt client id  

global redChannel,blueChannel,greenChannel

n=7          # no of LEDS
if sys.platform == "esp8266":
    print("cayenneWS2812B running on ESP8266")
    pin = 4   # connected to GPIO 4 on esp8266
else:
    print("cayenneWS2812B running on ESP32") 
    pin = 26   # connected to GPIO 21 on esp32
    
ledNoChannel = 0
redChannel   = 2
greenChannel = 3
blueChannel  = 4
global ledNo,red,green,blue
red=0
green=0
blue=0
ledNo = 0
neoPixel = neopixel.NeoPixel(Pin(pin), n)

# switch the LED off, it is too bright!

for i in range(7):
    neoPixel[0] = (red, green, blue)
neoPixel.write()
time.sleep(1)

# callback routine to treat command messages from Cayenne
def ledUpdate(message):
    global ledNo,red,green,blue
    msg = cayenne.client.CayenneMessage(message[0],message[1])
    if msg.channel == ledNoChannel:
        print("LED selected: ",msg.value)
        ledNo = int(msg.value)
    if msg.channel == redChannel:
        red=int(msg.value);
        print("Setting red to %d"%red)
    elif msg.channel == greenChannel:
        green=int(msg.value)
        print("Setting green to %d"%green)
    elif msg.channel == blueChannel:
        blue=int(msg.value)
        print("Setting blue to %d"%blue)
    print("writing the LED %d with r: %d, g: %d, b:%d"%(ledNo,red,green,blue))
    
    neoPixel[ledNo] = (green, red, blue)
    neoPixel.write() 
    return

client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO)
# register callback
client.on_message=ledUpdate

client.loop_forever()

#while True:
    #blue += 10;
    #if blue > 250:
        #blue = 0
    #neoPixel[0] = (red, green,blue)
    #neoPixel.write()
    #time.sleep(0.1)
