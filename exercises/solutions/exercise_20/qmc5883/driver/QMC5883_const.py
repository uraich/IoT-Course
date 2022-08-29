from micropython import const

QMC5883_ADDRESS = const(0x0d)
QMC5883_ID      = const(0xff)
GENEVA_MAG_DECLINATION = (2,35) # 2° 35'
X = const(0)   # indices of the data tuples corresponding to the x,y,z axis
Y = const(1)
Z = const(2)
# register definitions of QMC5883 magnetometer

QMC5883_DATA_X_LSB = const(0) 
QMC5883_DATA_X_MSB = const(1) 
QMC5883_DATA_Y_LSB = const(2) 
QMC5883_DATA_Y_MSB = const(3) 
QMC5883_DATA_Z_LSB = const(4) 
QMC5883_DATA_Z_MSB = const(5)
QMC5883_STATUS     = const(6)
QMC5883_TEMP_LSB   = const(7) 
QMC5883_TEMP_MSB   = const(8)
QMC5883_CTRL_1     = const(9)
QMC5883_CTRL_2     = const(0xa)
QMC5883_SET_PERIOD = const(0xb)
QMC5883_CHIP_ID    = const(0xc)

# Status register
QMC5883_STS_DRDY    = const(0)
QMC5883_STS_OVL     = const(1)
QMC5883_STS_DOR     = const(2)

# Control register 1

QMC5883_OSR_POS     = const(7)
QMC5883_OSR_SIZE    = const(2)
QMC5882_OSR_512     = const(0)
QMC5882_OSR_256     = const(1)
QMC5882_OSR_128     = const(2)
QMC5882_OSR_64      = const(3)
QMC5883_OVER_SAMPLING = {
    QMC5882_OSR_512: 512,
    QMC5882_OSR_256: 256,
    QMC5882_OSR_128: 128,
    QMC5882_OSR_64 : 64}


QMC5883_RNG_POS     = const(5)
QMC5883_RNG_SIZE    = const(2)
QMC5883_2G          = const(0)
QMC5883_8G          = const(1)
QMC5883_RANGE = {
    QMC5883_2G : "2G",
    QMC5883_8G : "8G"}

QMC5883_ODR_POS     = const(4)
QMC5883_ODR_SIZE    = const(2)
QMC5883_10Hz        = const(0)
QMC5883_50Hz        = const(1)
QMC5883_100Hz       = const(2)
QMC5883_200Hz       = const(3)
QMC5883_OUTPUT_RATE = {
    QMC5883_10Hz  : "10 Hz",
    QMC5883_50Hz  : "50 Hz",
    QMC5883_100Hz : "100 Hz",
    QMC5883_200Hz : "200 Hz"}

QMC5883_MODE_POS    = const(1)
QMC5883_MODE_SIZE   = const(2)
QMC5883_MODE_STDBY  = const(0)
QMC5883_MODE_NORMAL = const(1)
QMC5883_MODE = {
    QMC5883_MODE_STDBY  : "standby",
    QMC5883_MODE_NORMAL : "normal"}
    
QMC5883_SOFT_RESET  = const(7)
QMC5883_ROL_PNT     = const(6)
QMC5883_INT_ENB     = const(0)

