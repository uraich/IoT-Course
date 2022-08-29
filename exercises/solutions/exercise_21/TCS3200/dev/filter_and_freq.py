# filter_and_freq.py: We want to get a feeling for the frequencies emitted by the TCS3200
# To measure these we will set the filters to clear and the frequency divider to 2%
# To make this work we need additional methods of the TCS3200 class
# allowing to set (and read back) the filters and the frequency divider
# This version of the driver only adds this additional functionality
#
# Copyright (c) U. Raich
# Written for the course on the Internet of Things at the
# University of Cape Coast, Ghana
# The program is released under the MIT licence

from machine import Pin

class TCS3200(object):
    """
    This class reads RGB values from a TCS3200 colour sensor.

    GND   Ground.
    VDD   Supply Voltage (2.7-5.5V)
    LED   1: LEDs on, 0: LEDs off
    /OE   Output enable, active low. When OE is high OUT is disabled
         allowing multiple sensors to share the same OUT line.
    OUT   Output frequency square wave.
    S0/S1 Output frequency scale selection.
    S2/S3 Colour filter selection.
    
    OUT is a square wave whose frequency is proprtional to the
    intensity of the selected filter colour.
    
    S2/S3 selects between red, green, blue, and no filter.
    
    S0/S1 scales the frequency at 100%, 20%, 2% or off.
    
    To take a reading the colour filters are selected in turn for a
    fraction of a second and the frequency is read and converted to
    Hz.
    
    Default connections:
    TCS3200 WeMos GPIO
      S0     D3   17 
      S1     D4   16
      S2     D8   05
      S3     D5   18
      OUT    D6   19
      LED    D7   23
      OE     GND  
    """
    # class variables
    
    ON  = True  # on for debugging and the leds
    OFF = False # off

    RED   = (0,0) # S2 and S3 low
    BLUE  = (0,1) # S2 low, S3 high
    GREEN = (1,1) # S2 and S3 high
    CLEAR = (1,0) # S2 high and S3 low

    POWER_OFF       = (0,0) # S0 and S1 low
    TWO_PERCENT     = (0,1) # S0 low, S1 high
    TWENTY_PERCENT  = (1,0) # S0 high, S1 low
    HUNDRED_PERCENT = (1,1) # S0 and S1 high
    
    def __init__(self, OUT=19, S2=5, S3=18, S0=None, S1=None, LED=None,OE=None):
        """
        The gpios connected to the sensor OUT, S2, and S3 pins must
        be specified.  The S0, S1 (frequency) and LED and OE (output enable) 
        gpios are optional.
        The OE pin is missing on some TCS3200 boards
        """
        
        self._OUT = Pin(OUT,Pin.IN,Pin.PULL_UP)
        
        self._S2 = Pin(S2,Pin.OUT)
        self._S3 = Pin(S3,Pin.OUT)
        
        self._S0  = S0
        self._S1  = S1
        self._OE  = OE
        self._LED = LED
        
        
        if S0 and S1 :
            self._S0 = Pin(S0,Pin.OUT)
            self._S1 = Pin(S1,Pin.OUT)
            
        if LED :
            self._LED = Pin(LED,Pin.OUT)
            self._LED.on()
                
        if OE :
            self._OE =  Pin(OE,Pin.OUT)

        self._debug = self.OFF
        
        
    @property
    def debugging(self) :
        return self._debug
        
    @debugging.setter
    def debugging(self,onOff) :
        if onOff:
            print("Debugging switched on")
        else :
            print("Debugging switched off")
        self._debug = onOff

    # controls the illumination LEDs
    @property
    def led(self):
        # get the current state of the illumination leds
        return self._LED.value()
    
    @led.setter
    def led(self,onOff):
        if onOff:
            self._LED.on()
        else:
            self._LED.off()
            
    # sets the filters
    @property
    def filter(self):
        current_setting = (self._S2.value(),self._S3.value())
        if self._debug:
            if current_setting == self.RED:
                print("Red filter is set")
            elif current_setting == self.GREEN:
                print("Green filter is set")
            elif current_setting == self.BLUE :
                print("Blue filter is set")
            else:
                print("No filters are set. The filter setting is clear")
        return current_setting      
    
    @filter.setter
    def filter(self,filter_setting):
        if self._debug:
            print("Setting S2 to {:d} and S3 to {:d}".format(filter_setting[0],filter_setting[1]))
        self._S2.value(filter_setting[0])
        self._S3.value(filter_setting[1])

    @property
    def freq_divider(self):
        if not self._S0 or not self._S1:
            print("S0 or S1 signal is not connected. The frequency divider is therefore fixed")
            return
        
        current_freq_div = (self._S0.value(),self._S1.value())
        if self._debug:
            if current_freq_div == self.POWER_OFF:
                print("Device set to sleep mode")
            elif current_freq_div == self.TWO_PERCENT:
                print("Frequency divided by a factor 50")
            elif current_freq_div == self.TWENTY_PERCENT:
                print("Frequency divided by a factor 5")
            else:
                print("Frequency at 100%")

        return current_freq_div
    
    @freq_divider.setter
    def freq_divider(self,freq_div):
        if not self._S0 or not self._S1:
            print("S0 or S1 signal is not connected. The frequency divider is therefore fixed and cannot be set")
            return
        
        if self._debug:
            print("Setting S0 to {:d} and S1 to {:d}".format(freq_div[0],freq_div[1]))
        self._S0.value(freq_div[0])
        self._S1.value(freq_div[1])
    
# This part is the main project and should later go into a separate file

# create an TCS3200 object
tcs3200 = TCS3200(OUT=19, S2=5, S3=18, S0=17, S1=16, LED=23)

# set debugging on
tcs3200.debugging=tcs3200.ON

# switch the LEDs on
tcs3200.led = tcs3200.ON

# set the filters to clear and read the settings back
tcs3200.filter=tcs3200.CLEAR
print(tcs3200.filter)
if tcs3200.filter == tcs3200.CLEAR:
    print("Filter is set to CLEAR")
else:
    print("Something went wrong when setting the filter")

# Set the frequency divider to 2% and read it back
tcs3200.freq_divider=tcs3200.TWO_PERCENT
print(tcs3200.freq_divider)
if tcs3200.freq_divider == tcs3200.TWO_PERCENT:
    print("Frequency divider is set to 2%")
else:
    print("Something went wrong when setting the frequency divider")
