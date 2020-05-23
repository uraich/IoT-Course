from machine import I2C, Pin
import sys,time
import errno
import math
__version__ = '1.0'
__author__ = 'Uli Raich'
__license__ = "GNU General Public License"

# I2C address B 0x45 ADDR (pin 2) connected to VDD
DEFAULT_I2C_ADDRESS = 0x45

if sys.platform == "esp8266":
#    print("Running on ESP8266")
    pinScl      =  5  #ESP8266 GPIO5 (D1
    pinSda      =  4  #ESP8266 GPIO4 (D2)
else:
#    print("Running on ESP32") 
    pinScl      =  22  # SCL on esp32 
    pinSda      =  21  # SDA ON ESP32

class SHT3X:
    POLYNOMIAL  = 0x131 # P(x) = x^8 + x^5 + x^4 + 1 = 100110001
    CMD_READ_SERIALNBR  = b'\x37\x80' # read serial number
    CMD_READ_STATUS     = b'\xF3\x2D' # read status register
    CMD_CLEAR_STATUS    = b'\x30\x41' # clear status register
    CMD_HEATER_ENABLE   = b'\x30\x6D' # enabled heater
    CMD_HEATER_DISABLE  = b'\x30\x66' # disable heater
    CMD_SOFT_RESET      = b'\x30\xA2' # soft reset
    CMD_GENERAL_RESET   = b'\x00\x06' # general (hard) reset
    CMD_BREAK           = b'\x30\x93' # stop periodic measurement
    CMD_ART             = b'\x2b\x32' # accelerated response time

    CMD_FETCH_DATA      = b'\xE0\x00' # readout measurements for periodic mode
    CMD_R_AL_LIM_LS     = b'\xE1\x02' # read alert limits, low set
    CMD_R_AL_LIM_LC     = b'\xE1\x09' # read alert limits, low clear
    CMD_R_AL_LIM_HS     = b'\xE1\x1F' # read alert limits, high set
    CMD_R_AL_LIM_HC     = b'\xE1\x14' # read alert limits, high clear
    CMD_W_AL_LIM_HS     = b'\x61\x1D' # write alert limits, high set
    CMD_W_AL_LIM_HC     = b'\x61\x16' # write alert limits, high clear
    CMD_W_AL_LIM_LC     = b'\x61\x0B' # write alert limits, low clear
    CMD_W_AL_LIM_LS     = b'\x61\x00' # write alert limits, low set
    CMD_NO_SLEEP        = b'\x30\x3E'

    CMD_ALERT_READ      = b'\xe1\x00' # read alert limits
    CMD_ALERT_WRITE     = b'\x61\x00' # write alert limits

    # status register bits
    ALERT               = 0x8000
    HEATER              = 0x2000
    RH_ALERT            = 0x0800
    T_ALERT             = 0x0400
    RESET               = 0x0010
    COMMAND_STATUS      = 0x0002
    CHKSUM_STATUS       = 0x0001
    
    REP_S_HIGH          = 0
    REP_S_MEDIUM        = 1
    REP_S_LOW           = 2

    REP_P_HIGH          = 2
    REP_P_MEDIUM        = 1
    REP_P_LOW           = 0
    
    CLOCK_STRETCH       = 1
    NO_CLOCK_STRETCH    = 0
    CMD_MEAS            = b'\x24\x00' # base measurement command

    
    # 3 bit CRC for the measurement commands
    crc3 = {0x2C00: 6,
            0x2c08: 5,
            0x2c10: 0,
            0x2400: 0,
            0x2408: 3,
            0x2410: 6}

    measDuration = { REP_S_LOW   : 4,
                     REP_S_MEDIUM: 6,
                     REP_S_HIGH:  15}

    CMD_MEAS_PERIODIC    = b'\x20\x20' # base periodic measurement command

    crc3Periodic = {0x2030: 2,
                    0x2020: 4,
                    0x2028: 7,
                    0x2130: 0,
                    0x2120: 6,
                    0x2128: 5,
                    0x2330: 4,
                    0x2320: 2,
                    0x2328: 1,
                    0x2730: 7,
                    0x2720: 1,
                    0x2728: 2}
    mpsCode = {0.5: 0,
               1.0: 1,
               2.0: 2,
               4.0: 3,
               10.0: 7}
    
    crc3AlertRead  = {0xe118: 7,
                      0xe110: 4,
                      0xe108: 1,
                      0xe100: 2}
    
    crc3AlertWrite = {0x6118: 5,
                      0x6110: 6,
                      0x6108: 3,
                      0x6100: 0}
    
    #=============================================================================
    # Initializes the I2C bus for communication with the sensor.
    #-----------------------------------------------------------------------------
    # input: i2cAddress    I2C address, 0x44 ADDR pin low / 0x45 ADDR pin high
    #-----------------------------------------------------------------------------
    def __init__(self, scl_pin=pinScl, sda_pin=pinSda, i2c_address=DEFAULT_I2C_ADDRESS):
#        print("sda: ",pinSda," scl: ",pinScl)
        if sys.platform == "esp8266":
            self.i2c = I2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        else:
            self.i2c = I2C(1,scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.i2c_addr = i2c_address
        time.sleep_ms(50)
        if not self.isPresent():
            raise SHT3XError(SHT3XError.BUS_ERROR)
        
    def isPresent(self):
        """
        Return true if the sensor is correctly connected, False otherwise
        """
        return self.i2c_addr in self.i2c.scan()
        
    def _calcCrc(self, data):
        # calculates 8-Bit checksum with given polynomial
        crc = 0xFF
        
        for b in data[0:2]:
            crc ^= b;
            for _ in range(8, 0, -1):
                if crc & 0x80:
                    crc = (crc << 1) ^ SHT3X.POLYNOMIAL;
                else:
                    crc <<= 1
        return crc
    
    def _checkCrc(self,data):
        crc = self._calcCrc(data)
        crc_to_check = data[-1]       
        return crc_to_check == crc
    
    def _sendCmdPoll(self, cmd_request, response_size=6, timeout=100):
        """
        Send a command to the sensor polls for the answer in intervals of 1 ms
        Raises a TIMEOUT exception it does not get an answer before the timeout is reached
        The response data is validated by CRC
        This call is only valid for 
        """
        # check if this is a comand valid for polling
        if cmd_request[0] < 0x20 or cmd_request[0] > 0x27:
            raise SHT3XError(SHT3XError.WRONG_CMD)
        # try sending the command
        try:
            self.i2c.writeto(self.i2c_addr, cmd_request)
        except OSError as exception:
            if exception.args[0] == errno.ENODEV:
                raise SHT3XError(SHT3XError.BUS_ERROR)
            raise exception
        to=timeout
        while True:
            try:
                time.sleep_ms(1)
                data = self.i2c.readfrom(self.i2c_addr, 6)
                if data != None:
                    break
            except OSError as exception:
                to -= 1
                if to == 0:
                    raise SHT3XError(SHT3XError.TIMEOUT)
                # print(exception)
                
        for i in range(response_size//3):
            if not self._checkCrc(data[i*3:(i+1)*3]): # pos 2 and 5 are CRC
                raise SHT3XError(SHT3XError.CRC_ERROR)
        if data == bytearray(response_size):
            raise SHT3XError(SHT3XError.DATA_ERROR)       
        return data
    
    def _sendCmd(self, cmd_request, response_size=6, delay_ms=100):
        """
        Send a command to the sensor and read (optionally) the response
        The response data is validated by CRC
        """
        try:
            # print("sendCmd: cmd = ",hex(cmd_request[0]),hex(cmd_request[1]))
            self.i2c.writeto(self.i2c_addr, cmd_request)
            if not response_size:
                time.sleep_ms(delay_ms)
                return
            time.sleep_ms(delay_ms)
            data = self.i2c.readfrom(self.i2c_addr, response_size)
            for i in range(response_size//3):
                if not self._checkCrc(data[i*3:(i+1)*3]): # pos 2 and 5 are CRC
                    raise SHT3XError(SHT3XError.CRC_ERROR)
            if data == bytearray(response_size):
                raise SHT3XError(SHT3XError.DATA_ERROR)
            return data
        except OSError as exception:
            if exception.args[0] == errno.ENODEV:
                raise SHT3XError(SHT3XError.BUS_ERROR)
            raise exception

    def serialNumber(self):
        data = self._sendCmd(self.CMD_READ_SERIALNBR,delay_ms=2)
        nr = data[0] << 24 | data[1] << 16 | data[3] << 8 | data[4]
        return nr
    
    def setART(self):
        self._sendCmd(self.CMD_ART,None,delay_ms=2)
        return
    
    def readStatus(self,raw=False):
        """
        Get the sensor status register. 
        It returns an int value or the bytearray(3) if raw==True
        """
        data = self._sendCmd(self.CMD_READ_STATUS, 3, delay_ms=20); 
        if raw:
            return data
        status = data[0] << 8 | data[1]
        return status
    
    def clearStatus(self):
        """
        clear the status register
        """
        return self._sendCmd(self.CMD_CLEAR_STATUS, None);
    
    def printStatus(self):
        status = self.readStatus()
        print("--------------------------------------------------")
        print("Status register content: ",hex(status))
        print("--------------------------------------------------")
        if status & self.ALERT:
            print("Alert pending")
            if status & self.RH_ALERT and status & self.T_ALERT:
                print("Alert is both, temperature and humidity alert")
            else:
                if status & self.T_ALERT:
                    print("Alert is temperature alert")
                if status & self.RH_ALERT:
                    print("Alert is humidity alert")                    
        else:
            print("No alert pending")
            
        if status & self.HEATER:
            print("Heater is enabled")
        else:
            print("Heater is disabled")

        if status & self.RESET:
            print("Reset detected")

        if status & self.COMMAND_STATUS:
            print("Last command failed")
        else:
            print("Last command succeeded")

        if status & self.CHKSUM_STATUS:
            print("Checksum of last write command was wrong")
        else:
            print("Checksum of last write command was correct")
        return
    
    def softReset(self,delay_ms=2):
        """
        Send a soft-reset to the sensor
        """
        self._sendCmd(self.CMD_SOFT_RESET, None)
        return
    
# This does not seem to work! Generates a bus error
#    def hardReset(self):
#        """
#        Send a hard general reset to the sensor
#        """
#        self._sendCmd(self.CMD_GENERAL_RESET, None);
        # must wait for min. 1.5 ms before the next command
#        time.sleep_ms(2)
#        return
    
    def startPeriodicMeas(self, mps=0.5, repeatability=None):
        measCmd = bytearray(self.CMD_MEAS_PERIODIC)
        if not repeatability:
            repeatability = self.REP_P_HIGH
        # print("base meas cmd: ",hex(measCmd[0]),hex(measCmd[1]))
        # print("mps code: ",hex(self.mpsCode[mps]))
        measCmd[0] |= self.mpsCode[mps]
        # print("repeatability << 3: ",hex(repeatability << 3))
        measCmd[1] |= repeatability << 3
        key = measCmd[0] << 8 | measCmd[1]
        # print("key: ",hex(key))
        measCmd[1] |= self.crc3Periodic[measCmd[0] << 8 | measCmd[1]]
        # print("meas cmd: ",hex(measCmd[0]),hex(measCmd[1]))
        # try sending the command
        try:
            self.i2c.writeto(self.i2c_addr, measCmd)
        except OSError as exception:
            if exception.args[0] == errno.ENODEV:
                raise SHT3XError(SHT3XError.BUS_ERROR)
            raise exception        
        return
    
    def stopPeriodicMeas(self):
        self._sendCmd(self.CMD_BREAK, None,delay_ms=2);   
        return
    
    def measPeriodic(self,mps=0.5, repeatability=None, raw=False, noOfMeas=50,callback=None):
        self.stopPeriodicMeas()
        delay = 1/mps
        print("Interval: ",delay)
        self.startPeriodicMeas(mps, repeatability)
        result=[]
        for i in range(noOfMeas):
            try:
                time.sleep_ms(math.ceil(delay*1000))
                # print("Fetching data, cmd= ",hex(self.CMD_FETCH_DATA[0]),hex(self.CMD_FETCH_DATA[1]))
                self.i2c.writeto(self.i2c_addr,self.CMD_FETCH_DATA)
                # print("after fetch cmd")
                data = self.i2c.readfrom(self.i2c_addr, 6)
            except OSError as exception:
                if exception.args[0] == errno.ENODEV:
                    raise SHT3XError(SHT3XError.BUS_ERROR)
                raise exception

            # checksum 
            for i in range(2):
                if not self._checkCrc(data[i*3:(i+1)*3]): # pos 2 and 5 are CRC
                    raise SHT3XError(SHT3XError.CRC_ERROR)
            if data == bytearray(6):
                raise SHT3XError(SHT3XError.DATA_ERROR)
            if callback:
                if raw:
                    callback(data)
                    result.append(data)
                else:
                    rawTemp=data[0] << 8 | data[1]
                    tempC = self._calcTemperatureCelsius(rawTemp)
                    rawHumi=data[3] << 8 | data[4]
                    humi = self._calcHumidity(rawHumi)
                    callback([tempC,humi])
                    # result.append([tempC,humi])
                    # print("Temperatur: ",tempC, "°C, Humidity: ",humi, "%")
                    
            if noOfMeas == 0:
                break
            
        self.stopPeriodicMeas()
        return result
            
    def getTempAndHumi(self, clockStretching=None, repeatability=None, raw=False, timeout=100):
        """
        If raw==True returns a bytearray(6) with sensor direct measurement otherwise
        It gets the temperature (T) and humidity (RH) measurement and returns them.
        
        The units are Celsius and percent
        Default repeatability is LOW and clock stretchin is on by default
        """
        
        if clockStretching == None:
            clockStretching = self.CLOCK_STRETCH
        if repeatability == None:
            repeatability = self.REP_S_LOW
        measCmd = bytearray(self.CMD_MEAS)
        measCmd[0] |= clockStretching << 3
        measCmd[1] |= repeatability << 3
        # print("Cmd: ",hex(measCmd[0]),hex(measCmd[1]))
        key = int(hex(measCmd[0]<<8 | measCmd[1]))
        # print("Type of key: ",type(key))
        measCmd[1] |= self.crc3[key]
        # print("key: ",key)
        # print("final cmd: ",hex(measCmd[0]),hex(measCmd[1]))
        
        if clockStretching:
            delay = self.measDuration[repeatability]
            # print("Repeatability: ",repeatability," Delay: ",delay,"ms")
            data = self._sendCmd(measCmd,6,delay_ms=delay)
        else:
            data = self._sendCmdPoll(measCmd,6,timeout)
        if raw:
            return data
        rawTemp=data[0] << 8 | data[1]
        tempC = self._calcTemperatureCelsius(rawTemp)
        rawHumi=data[3] << 8 | data[4]
        humi = self._calcHumidity(rawHumi)
        return [tempC,humi]
        
    def _calcTemperatureCelsius(self,rawTemp):
        tempC = -45.0 + 175.0*rawTemp/65536.0
        return tempC
        
    def _calcHumidity(self,rawHumi):
        return (100.0 * rawHumi/65536.0)

    def _tempC2tempRaw(self,tempC):
        return int((tempC+45.0)*65536.0/175.0)

    def _humi2humiRaw(self,humi):
        return int(humi*65536.0/100.0)
        
    def Celsius2Fahrenheit(self,tempC):
        """
        Convert temperature from Celsius to Fahrenheit
        """
        return 1.8*tempC + 32.0
    
    def Fahrenheit2Celsius(self,tempF):
        return (tempF-32.0)/1.8

    def enableHeater(self):
        """
        switch the heater on
        """
        return self._sendCmd(self.CMD_HEATER_ENABLE, None);
    
    def disableHeater(self):
        """
        switch the heater off
        """
        return self._sendCmd(self.CMD_HEATER_DISABLE, None);

    def readAlert(self,high=True,set=True,raw=False):
        readAlertCmd = bytearray(self.CMD_ALERT_READ)
        if high:
            if set:
                readAlertCmd[1] |= 0x018
            else:
                readAlertCmd[1] |= 0x010
        else:
            if not set:
                readAlertCmd[1] |= 0x08
        key = readAlertCmd[0] << 8 | readAlertCmd[1]
        readAlertCmd[1] |= self.crc3AlertRead[key]
        # print("readAlert command: ",hex(readAlertCmd[0]),hex(readAlertCmd[1]))
        data=self._sendCmd(readAlertCmd,response_size=3)        
        if raw:
            return data
        tmp = data[0] << 8 | data[1]
        # print("Returned raw data: ",hex(data[0]),",",hex(data[1]),", checksum: ",hex(data[2])) 
        # print("Returned alert high set: ",hex(tmp))
        humiRaw = tmp & 0xfe00
        tempRaw = (tmp << 7) & 0xff80
        temp = self._calcTemperatureCelsius(tempRaw)
        humi = self._calcHumidity(humiRaw)
        return [temp,humi]
    
    def writeAlert(self,tempC,humi,high=True,set=True):
        tempRaw=self._tempC2tempRaw(tempC)
        # print("Check temp: ",tempC," double convert: ",self._calcTemperatureCelsius(tempRaw))
        humiRaw=self._humi2humiRaw(humi)
        # print("Check humi: ",humi," double convert: ",self._calcHumidity(humiRaw))
        # print("TempRaw: ",hex(tempRaw))
        # print("HumiRaw: ",hex(humiRaw))      
        tempRaw &= 0xff80
        humiRaw &= 0xfe00
        alertLimit = humiRaw | (tempRaw >>7)
        # print("CombinedLimit: ",hex(alertLimit))
        alertBytes = [alertLimit>>8,alertLimit&0xff]
        # print(hex(alertBytes[0]),hex(alertBytes[1]))
        checksum = self._calcCrc(alertBytes)
        # print("checksum: ",hex(checksum))
        
        writeAlertCmd = bytearray(self.CMD_ALERT_WRITE)

        if high:
            if set:
                writeAlertCmd[1] |= 0x018
            else:
                writeAlertCmd[1] |= 0x010
        else:
            if not set:
                writeAlertCmd[1] |= 0x08
        key = writeAlertCmd[0] << 8 | writeAlertCmd[1]
        writeAlertCmd[1] |= self.crc3AlertWrite[key]
        # print("writeAlert command: ",hex(writeAlertCmd[0]),hex(writeAlertCmd[1]))
        
        writeAlertCmd.append(alertBytes[0])
        writeAlertCmd.append(alertBytes[1])
        writeAlertCmd.append(checksum)
        # for i in range(5):
            # print(hex(writeAlertCmd[i]))
        self.i2c.writeto(self.i2c_addr,writeAlertCmd)
        return
    
class SHT3XError(Exception):
    """
    Custom exception for errors on sensor management
    """
    BUS_ERROR  = 0x01 
    DATA_ERROR = 0x02
    CRC_ERROR  = 0x03
    TIMEOUT    = 0x04
    WRONG_CMD  = 0x05
    
    def __init__(self, error_code=None):
        self.error_code = error_code
        super().__init__(self.get_message())
    
    def get_message(self):
        if self.error_code == SHT3XError.BUS_ERROR:
            return "Bus error"
        elif self.error_code == SHT3XError.DATA_ERROR:
            return "Data error"
        elif self.error_code == SHT3XError.CRC_ERROR:
            return "CRC error"
        elif self.error_code == SHT3XError.WRONG_CMD:
            return "Cmd not allowed for polling"
        elif self.error_code == SHT3XError.TIMEOUT:
            return "Timeout"
        else:
            return "Unknown error"




