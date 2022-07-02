# dc_motor.py: a driver for the Lolin  HR8833 and AT8870 motor shields
from machine import Pin,I2C
from micropython import const
from utime import sleep_ms

HR8833_DEFAULT_I2C_ADDRESS = const(0x30)

class HR8833:

    GET_SLAVE_STATUS    = const(1)
    RESET_SLAVE         = const(2)
    CHANGE_I2C_ADDRESS  = const(3)
    CHANGE_STATUS       = const(4)
    CHANGE_FREQ         = const(5)
    CHANGE_DUTY         = const(6)

    STATUS_STOP         = const(0)
    STATUS_CCW          = const(1)
    STATUS_CW           = const(2)
    STATUS_SHORT_BRAKE  = const(3)
    STATUS_STANDBY      = const(4)
    
    CH_A                = const(0)
    CH_B                = const(1)
    CH_BOTH             = const(2)
    ON                  = True
    OFF                 = False
    
    def __init__(self,bus=1,scl=22,sda=21,i2c_adress=HR8833_DEFAULT_I2C_ADDRESS, debug=False) :
        self.debug = debug
        self.i2c_address = i2c_adress
        print("debug set to ",debug)
        
        # Create an I2C object
        # Check if can use the hardware I2C interface, if not, create a software I2C interface
        if bus == 1:
            if self.debug:
                print("Running on I2C hardware interface with bus = ",bus, "scl = ",scl, " sda = ",sda)
            self.i2c = I2C(bus,scl=Pin(scl),sda=Pin(sda))
        else:
            if self.debug:
                print("Running on I2C bus ",bus, "scl = ",scl, " sda = ",sda)
            self.i2c = SoftI2C(scl,sda)
            
        i2c_slaves = self.i2c.scan()
        if self.debug:
            if len(i2c_slaves) == 0:
                print("No I2C modules found")
            else:
                print("addresses found on the I2c bus: ",end = "")
                for i in range(len(i2c_slaves)):
                    print("0x{:02x} ".format(i2c_slaves[i]),end="")
                print("")
        if not self.i2c_address in i2c_slaves:
            raise Exception("Could not find the HR8833 motor shield on the I2C bus")

    def setDebug(self,onOff) :
        self.debug = onOff
        
    def readBytes(self,cmd,no_of_bytes) :
        buf = bytearray(1)
        buf[0] = cmd
        try:
            self.i2c.writeto(self.i2c_address,buf)  # send the command
        except:
            print("Cannot write 0x{:02x} to I2C address 0x{:02x}".format(cmd,self.i2c_address))
            return
        sleep_ms(50)                            # wait for response
        try:
            data = self.i2c.readfrom(self.i2c_address,2)
        except:
            print("Cannot read {:d} bytes from I2C address 0x{:02x}".format(no_of_bytes,self.i2c_address))
        return data

    def writeBytes(self,register,values) :
        buf = bytearray(len(values)+1)
        buf[0] = register
        buf[1:] = values[:]
        try:
            self.i2c.writeto(self.i2c_address,buf)
        except:
            print("Cannot write {:d} bytes to register 0x{:02x}".format(len(values),register))
        sleep_ms(50)
        try:
            data = self.i2c.readfrom(self.i2c_address,1)
        except:
            print("Cannot read {:d} bytes from I2C address 0x{:02x}".format(no_of_bytes,self.i2c_address))
        if self.debug:
            print("Return data: 0x{:02x}".format(data[0]))
        return data[0]
        
    def getInfo(self) :
        info = self.readBytes(self.GET_SLAVE_STATUS,2)
        if self.debug:
            print("Product ID: 0x{:02x}, version: 0x{:02x}".format(info[0],info[1]))
        return info

    def reset(self) :
        cmd = bytearray(1)
        cmd[0] = self.RESET_SLAVE
        try:
            self.i2c.writeto(self.i2c_address,cmd)
        except:
            print("Cannot send reset command to I2C bus")
        if self.debug:
            print("Motor controller was successfully reset")
        sleep_ms(500)          # give the motor controller time to come up again
        
    def changeStatus(self,channel,status):
        buf = bytearray(2)
        buf[0] = channel
        buf[1] = status
        self.writeBytes(self.CHANGE_STATUS,buf)

    def changeFreq(self,channel,freq) :
        buf = bytearray(4)
        buf[0] = channel
        buf[1] = freq & 0xff
        buf[2] = (freq >> 8) & 0xff
        buf[3] = (freq >> 16) & 0xff
        self.writeBytes(self.CHANGE_FREQ,buf)

    def changeDuty(self,channel,duty) :
        _duty = int(duty*100)
        buf = bytearray(3)
        buf[0] = channel
        buf[1] = _duty & 0xff
        buf[2] = (_duty >> 8) & 0xff
        self.writeBytes(self.CHANGE_DUTY,buf)
        
    def changeAddress(self,new_address) :
        buf = bytearray(1)
        buf[0] = new_address
        self.writeBytes(self.CHANGE_I2C_ADDRESS,buf)
