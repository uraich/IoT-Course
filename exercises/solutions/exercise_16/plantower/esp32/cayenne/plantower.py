#
# read out the plantower pms5003 dust sensor
# U. Raich, March 2021
#
# it is connected to
# Rx: D2 GPIO 21
# Tx: D1 GPIO 22

import machine,sys
try:
    import logging
except:
    import ulogging as logging

class PlanTower(object):
    PMS5003_MSG_LENGTH = 32
    MAGIC = 0x424d
    MAGIC_POS = 0
    FRAME_LENGTH_POS =  2
    PM1_0_STD_POS    =  4
    PM2_5_STD_POS    =  6
    PM10_STD_POS     =  8

    PM1_0_ATM_POS    = 10
    PM2_5_ATM_POS    = 12
    PM10_ATM_POS     = 14

    BEYOND_0_3_POS   = 16
    BEYOND_0_5_POS   = 18
    BEYOND_1_0_POS   = 20
    BEYOND_2_5_POS   = 22
    BEYOND_5_0_POS   = 24
    BEYOND_10_POS    = 26   
    RESERVED         = 28
    CHKSUM_POS       = 30
    
    def __init__(self):
        self.log = logging.getLogger("PlanTower")
        self.log.setLevel(logging.ERROR)
        self.uart2 = machine.UART(2, baudrate=9600, rx=22, tx=21, timeout=10000)
        self.count = 0
        self.clear_sums()
        
    def read_raw(self):
        self.rawline = self.uart2.read(self.PMS5003_MSG_LENGTH)
        self.rawline_txt = ['']*2
        try:
            for i in range(self.PMS5003_MSG_LENGTH//2):
                self.rawline_txt[0] += '0x{:02x} '.format(self.rawline[i])
            for i in range(self.PMS5003_MSG_LENGTH//2,self.PMS5003_MSG_LENGTH):
                self.rawline_txt[1] += '0x{:02x} '.format(self.rawline[i])

            self.log.debug(self.rawline_txt[0])
            self.log.debug(self.rawline_txt[1])
        except:
            self.log.error("Cannot read PlanTower sensor. Is its Tx line (Pin 5) connected to GPIO 22?")
            sys.exit()            

    def decode(self):
        if not self.check_magic:
            self.log.error("Not a valid PlanTower message")
            sys.exit()
        else:
            self.log.debug("Found a valid PlanTower message")

        self.frame_length = (self.rawline[self.FRAME_LENGTH_POS] << 8) |  self.rawline[self.FRAME_LENGTH_POS+1]
        self.log.debug('frame length: {:04d}'.format(self.frame_length))
        if self.frame_length != self.PMS5003_MSG_LENGTH - 4:
            self.log.error('Message with wrong frame length from PlanTower sensor')
            sys.exit()
        if not self.check_chksum():
            self.log.error('Bad checksum: Calculated: 0x{:04x} read: 0x{:04x}'.format(self.calculated_chk_sum,
                                                                                      self.read_chksum))
            self.exit()
        else:
            self.log.debug("Checksum ok!")

        self.pm1_0_std = (self.rawline[self.PM1_0_STD_POS] << 8) | self.rawline[self.PM1_0_STD_POS+1]
        self.pm2_5_std = (self.rawline[self.PM2_5_STD_POS] << 8) | self.rawline[self.PM2_5_STD_POS+1]
        self.pm10_std  = (self.rawline[self.PM10_STD_POS] << 8) | self.rawline[self.PM10_STD_POS+1]

        self.pm1_0_atm = (self.rawline[self.PM1_0_ATM_POS] << 8) | self.rawline[self.PM1_0_ATM_POS+1]
        self.pm2_5_atm = (self.rawline[self.PM2_5_ATM_POS] << 8) | self.rawline[self.PM2_5_ATM_POS+1]
        self.pm10_atm  = (self.rawline[self.PM10_ATM_POS] << 8)  | self.rawline[self.PM10_ATM_POS+1]
        
        self.beyond_0_3 = (self.rawline[self.BEYOND_0_3_POS] << 8) | self.rawline[self.BEYOND_0_3_POS+1]
        self.beyond_0_5 = (self.rawline[self.BEYOND_0_5_POS] << 8) | self.rawline[self.BEYOND_0_5_POS+1]
        self.beyond_1_0 = (self.rawline[self.BEYOND_1_0_POS] << 8) | self.rawline[self.BEYOND_1_0_POS+1]
        self.beyond_2_5 = (self.rawline[self.BEYOND_2_5_POS] << 8) | self.rawline[self.BEYOND_2_5_POS+1]
        self.beyond_5_0 = (self.rawline[self.BEYOND_5_0_POS] << 8) | self.rawline[self.BEYOND_5_0_POS+1]
        self.beyond_10  = (self.rawline[self.BEYOND_10_POS] << 8) | self.rawline[self.BEYOND_10_POS+1]

        
    def check_chksum(self):
        self.calculated_chksum = 0
        for i in range(self.PMS5003_MSG_LENGTH-2):
            self.calculated_chksum += self.rawline[i]
        self.log.debug('Calculated checksum: 0x{:04x}'.format(self.calculated_chksum))
        self.read_chksum = (self.rawline[self.CHKSUM_POS] << 8) | self.rawline[self.CHKSUM_POS+1]
                                                       
        self.log.debug('Checksum read from sensor: 0x{:04x}'.format(self.read_chksum))
        if self.calculated_chksum == self.read_chksum:
            return True
        else:
            return False
        
    def check_magic(self):
        if self.line[self.MAGIC_POS] != 0x42 or self.line[self.MAGIC_POS+1] != 0x4d:
            return False
        else:
            return True
        
    def print_results(self):
        print('PM 1.0 concentration (CF = 1, standard particle): {:d} ug/m3'.format(self.pm1_0_std))
        print('PM 2.5 concentration (CF = 1, standard particle): {:d} ug/m3'.format(self.pm2_5_std))
        print('PM 10  concentration (CF = 1, standard particle): {:d} ug/m3'.format(self.pm10_std))

        print('PM 1.0 concentration (under atmospheric environment): {:d} ug/m3'.format(self.pm1_0_atm))
        print('PM 2.5 concentration (under atmospheric environment): {:d} ug/m3'.format(self.pm2_5_atm))
        print('PM 10  concentration (under atmospheric environment): {:d} ug/m3'.format(self.pm10_atm))
       
        print('No of particle with diameter beyond 0.3 um in 0.1L of air: {:d}'.format(self.beyond_0_3))
        print('No of particle with diameter beyond 0.5 um in 0.1L of air: {:d}'.format(self.beyond_0_5))
        print('No of particle with diameter beyond 1.0 um in 0.1L of air: {:d}'.format(self.beyond_1_0))
        print('No of particle with diameter beyond 2.5 um in 0.1L of air: {:d}'.format(self.beyond_2_5))
        print('No of particle with diameter beyond 5.0 um in 0.1L of air: {:d}'.format(self.beyond_5_0))
        print('No of particle with diameter beyond 10  um in 0.1L of air: {:d}'.format(self.beyond_10))

    def print_avr_results(self):
        print("Average results over %d seconds"%self.count)
        print('PM 1.0 concentration (CF = 1, standard particle): {:f} ug/m3'.format(self.pm1_0_std_avr/self.count))
        print('PM 2.5 concentration (CF = 1, standard particle): {:f} ug/m3'.format(self.pm2_5_std_avr/self.count))
        print('PM 10  concentration (CF = 1, standard particle): {:f} ug/m3'.format(self.pm10_std_avr/self.count))

        print('PM 1.0 concentration (under atmospheric environment): {:f} ug/m3'.format(self.pm1_0_atm_avr/self.count))
        print('PM 2.5 concentration (under atmospheric environment): {:f} ug/m3'.format(self.pm2_5_atm_avr/self.count))
        print('PM 10  concentration (under atmospheric environment): {:f} ug/m3'.format(self.pm10_atm_avr/self.count))
       
        print('No of particle with diameter beyond 0.3 um in 0.1L of air: {:f}'.format(self.beyond_0_3_avr/self.count))
        print('No of particle with diameter beyond 0.5 um in 0.1L of air: {:f}'.format(self.beyond_0_5_avr/self.count))
        print('No of particle with diameter beyond 1.0 um in 0.1L of air: {:f}'.format(self.beyond_1_0_avr/self.count))
        print('No of particle with diameter beyond 2.5 um in 0.1L of air: {:f}'.format(self.beyond_2_5_avr/self.count))
        print('No of particle with diameter beyond 5.0 um in 0.1L of air: {:f}'.format(self.beyond_5_0_avr/self.count))
        print('No of particle with diameter beyond 10  um in 0.1L of air: {:f}'.format(self.beyond_10_avr/self.count))
        
    def sum(self):
        # average results over 1 min
        self.pm1_0_std_avr += self.pm1_0_std
        self.pm2_5_std_avr += self.pm2_5_std
        self.pm10_std_avr  += self.pm10_std

        self.pm1_0_atm_avr += self.pm1_0_atm
        self.pm2_5_atm_avr += self.pm2_5_atm
        self.pm10_atm_avr  += self.pm10_atm

        self.beyond_0_3_avr += self.beyond_0_3
        self.beyond_0_5_avr += self.beyond_0_5
        self.beyond_1_0_avr += self.beyond_1_0
        self.beyond_2_5_avr += self.beyond_2_5
        self.beyond_5_0_avr += self.beyond_5_0
        self.beyond_10_avr  += self.beyond_10

        self.count += 1

    def clear_sums(self):
        self.pm1_0_std_avr = 0
        self.pm2_5_std_avr = 0
        self.pm10_std_avr  = 0

        self.pm1_0_atm_avr = 0
        self.pm2_5_atm_avr = 0
        self.pm10_atm_avr  = 0

        self.beyond_0_3_avr = 0
        self.beyond_0_5_avr = 0
        self.beyond_1_0_avr = 0
        self.beyond_2_5_avr = 0
        self.beyond_5_0_avr = 0
        self.beyond_10_avr  = 0

        self.count = 0
