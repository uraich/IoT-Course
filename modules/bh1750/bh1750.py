# A class for the BH11750 ambient light sensor
# written for the course on the Internet of Things at the
# University of Cape Coast, Ghana
# This program is written for MicroPython on an ESP32 
# The card used is a LoLin Ambient Light sensor shield of WeMos D1 mini series
# U. Raich, May 2020

__version__ = '0.1.0'
__author__ = 'Uli Raich'
__license__ = "GNU General Public License"
from machine import Pin,I2C
import time,sys
import errno

# I2C address B 0x45 ADDR (pin 2) connected to VDD
DEFAULT_I2C_ADDRESS = 0x23

if sys.platform == "esp8266":
#    print("Running on ESP8266")
    pinScl      =  5  #ESP8266 GPIO5 (D1
    pinSda      =  4  #ESP8266 GPIO4 (D2)
else:
#    print("Running on ESP32") 
    pinScl      =  22  # SCL on esp32 
    pinSda      =  21  # SDA ON ESP32

class BH1750():
    """ Implement BH1750 communication. """
    # Define some constants from the datasheet
    POWER_DOWN = b'\x00' # No active state
    POWER_ON   = b'\x01' # Power on
    RESET      = b'\x07' # Reset data register value
    # Measurement durations
    LOW_RES_WAIT  = 16
    HIGH_RES_WAIT = 120
    HIGH_RES_CODE = 3
    # Start measurement at 4lx resolution. Time typically 16ms.
    CONTINUOUS_LOW_RES_MODE = b'\x13'
    # Start measurement at 1lx resolution. Time typically 120ms
    CONTINUOUS_HIGH_RES_MODE_1 = b'\x10'
    # Start measurement at 0.5lx resolution. Time typically 120ms
    CONTINUOUS_HIGH_RES_MODE_2 = b'\x11'
    # Start measurement at 1lx resolution. Time typically 120ms
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_HIGH_RES_MODE_1 = b'\x20'
    # Start measurement at 0.5lx resolution. Time typically 120ms
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_HIGH_RES_MODE_2 = b'\x21'
    # Start measurement at 1lx resolution. Time typically 120ms
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_LOW_RES_MODE = b'\x23'

    def __init__(self, scl_pin=pinScl, sda_pin=pinSda, delta_temp = 0, delta_hum = 0,i2c_address=DEFAULT_I2C_ADDRESS):
#        print("sda: ",pinSda," scl: ",pinScl)
        if sys.platform == "esp8266":
            self.i2c = I2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        else:
            self.i2c = I2C(1,scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.i2c_addr = i2c_address
        self.powerDown()
        self.setSensitivity()
        
    def isPresent(self):
        """
        Return true if the sensor is correctly connected, False otherwise
        """
        return self.i2c_addr in self.i2c.scan()
    
    def _sendCmd(self, cmd_request):
        """
        Send a command to the sensor

        """
        try:
            self.i2c.writeto(self.i2c_addr, cmd_request)
            return
        
        except OSError as ex:
            if ex.args[0] == errno.ENODEV:
                raise BH1750Error(BH1750Error.BUS_ERROR)
            raise ex
        
    def _setMode(self, mode):
        self.mode = mode
        self._sendCmd(self.mode)

    def powerDown(self):
        self._setMode(self.POWER_DOWN)

    def powerUp(self):
        self._setMode(self.POWER_ON)

    def reset(self):
        self.powerUp() #It has to be powered on before resetting
        self._setMode(self.RESET)

    def contLowRes(self):
        self._setMode(self.CONTINUOUS_LOW_RES_MODE)

    def contHighRes(self):
        self._setMode(self.CONTINUOUS_HIGH_RES_MODE_1)

    def contHighRes2(self):
        self._setMode(self.CONTINUOUS_HIGH_RES_MODE_2)

    def oneTimeLowRes(self):
        self._setMode(self.ONE_TIME_LOW_RES_MODE)

    def oneTime_high_res(self):
        self._setMode(self.ONE_TIME_HIGH_RES_MODE_1)

    def oneTimeHighRes2(self):
        self._setMode(self.ONE_TIME_HIGH_RES_MODE_2)

    def setSensitivity(self, sensitivity=69):
        """ Set the sensor sensitivity.
            Valid values are 31 (lowest) to 254 (highest), default is 69.
        """
        if sensitivity < 31:
            self.mtreg = 31
        elif sensitivity > 254:
            self.mtreg = 254
        else:
            self.mtreg = sensitivity
        self.powerUp()

        self._setMode((0x40 | (self.mtreg >> 5)).to_bytes(1,'big'))
        self._setMode((0x60 | (self.mtreg & 0x1f)).to_bytes(1,'big'))
        self.powerDown()

    def getResult(self):
        """ Return current measurement result in lx. """
        self.i2c.writeto(self.i2c_addr, self.mode)
        data = int.from_bytes(self.i2c.readfrom(self.i2c_addr, 2),'big')            

        # print("data read out: ",hex(data)," ",data)
        mode2coeff =  2 if (int.from_bytes(self.mode,1,'big') & 0x03) == 0x01 else 1
        # print("mode2coeff : ",mode2coeff, " mtreg: ",self.mtreg)
        ratio = 1/(1.2 * (self.mtreg/69.0) * mode2coeff)
        # print("ratio: ",ratio)
        return ratio*data

    def waitForResult(self, additional=0):
        if int.from_bytes(self.mode,'big') & self.HIGH_RES_CODE == 3:
            # max values according to data sheet
            basetime = 24
        else:
            basetime = 180
#        print("basetime: ",basetime)
#        print("mtreg: ",self.mtreg)
#        print("additional time: ",additional)
#        print("Wait: ",int(basetime * (self.mtreg/69.0) + additional))
        time.sleep_ms(int(basetime * (self.mtreg/69.0) + additional))

    def doMeasurement(self, mode, additional_delay=0):
        """ 
        Perform complete measurement using command
        specified by parameter mode with additional
        delay specified in parameter additional_delay.
        Return output value in Lx.
        """
        self.reset()
        self._setMode(mode)
        self.waitForResult(additional=additional_delay)
        return self.getResult()
    
    def doMeasurementOneTime(self, mode, additional_delay=0):
        """ 
        Perform complete measurement using command
        specified by parameter mode with additional
        delay specified in parameter additional_delay.
        Return output value in Lx.
        """
        self._setMode(mode)
        self.waitForResult(additional=additional_delay)
        return self.getResult()
    
    def measureOneTimeLowRes(self, additional_delay=0):
        return self.doMeasurementOneTime(self.ONE_TIME_LOW_RES_MODE, additional_delay)

    def measureOneTimeHighRes(self, additional_delay=0):
        return self.doMeasurementOneTime(self.ONE_TIME_HIGH_RES_MODE_1, additional_delay)

    def measureOneTimeHighRes2(self, additional_delay=0):
        return self.doMeasurementOneTime(self.ONE_TIME_HIGH_RES_MODE_2, additional_delay)
    
    def measureContLowRes(self, additional_delay=0):
        return self.doMeasurement(self.CONTINUOUS_LOW_RES_MODE, additional_delay)

    def measureContHighRes(self, additional_delay=0):
        return self.doMeasurement(self.CONTINUOUS_HIGH_RES_MODE_1, additional_delay)

    def measureContHighRes2(self, additional_delay=0):
        return self.doMeasurement(self.CONTINUOUS_HIGH_RES_MODE_2, additional_delay)
    
class BH1750Error(Exception):
    """
    Custom exception for errors on sensor management
    """
    BUS_ERROR = 0x01 

    def __init__(self, error_code=None):
        self.error_code = error_code
        super().__init__(self.get_message())
    
    def get_message(self):
        if self.error_code == BH1750Error.BUS_ERROR:
            return "Bus error"
        else:
            return "Unknown error"


        
