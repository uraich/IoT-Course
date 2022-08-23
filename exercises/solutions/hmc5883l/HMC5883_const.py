from micropython import const

HMC5883_ADDRESS = const(0x1e)
GENEVA_MAG_DECLINATION = (2,35) # 2° 35'
# register definitions of HMC5883 magnetometer

HMC5883_CONF_A     = const(0)
HMC5883_CONF_B     = const(1)
HMC5883_MODE       = const(2)
HMC5883_DATA_X_MSB = const(3) 
HMC5883_DATA_X_LSB = const(4) 
HMC5883_DATA_Y_MSB = const(5) 
HMC5883_DATA_Y_LSB = const(6) 
HMC5883_DATA_Z_MSB = const(7) 
HMC5883_DATA_Z_LSB = const(8)
HMC5883_STATUS     = const(9)
HMC5883_ID_A       = const(10)
HMC5883_ID_B       = const(11)
HMC5883_ID_C       = const(12)

# config A register
HMC5883_MA_POS     = const(6)
HMC5883_MA_SIZE    = const(2)
HMC5883_AVG_1      = const(0)
HMC5883_AVG_2      = const(1)
HMC5883_AVG_4      = const(2)
HMC5883_AVG_8      = const(3) # default

HMC5883_average = {
    HMC5883_AVG_1 : 1,
    HMC5883_AVG_2 : 2,
    HMC5883_AVG_4 : 4,
    HMC5883_AVG_8 : 8}

HMC5883_DO_POS     = const(4)
HMC5883_DO_SIZE    = const(3)
HMC5883_RATE_0_75  = const(0)
HMC5883_RATE_1_5   = const(1)
HMC5883_RATE_3     = const(2)
HMC5883_RATE_7_5   = const(3)
HMC5883_RATE_15    = const(4) # default
HMC5883_RATE_30    = const(5)
HMC5883_RATE_75    = const(6)

HMC5883_dataRate = {
    HMC5883_RATE_0_75 : 0.75,
    HMC5883_RATE_1_5  : 1.5,
    HMC5883_RATE_3    : 3.0,
    HMC5883_RATE_7_5  : 7.5,
    HMC5883_RATE_15   : 15,
    HMC5883_RATE_30   : 30.0,
    HMC5883_RATE_75   : 75.0}

HMC5883_MS_POS         = const(1)
HMC5883_MS_SIZE        = const(2)
HMC5883_MS_NORMAL_BIAS = const(0) # default
HMC5883_MS_POS_BIAS    = const(1)
HMC5883_MS_NEG_BIAS    = const(2)
HMC5883_bias = {
    HMC5883_MS_NORMAL_BIAS: "normal bias",
    HMC5883_MS_POS_BIAS:    "positive bias",
    HMC5883_MS_NEG_BIAS:    "negative bias"}

# config B register
HMC5883_GAIN_POS   = const(7)
HMC5883_GAIN_SIZE  = const(3)
HMC5883_GAIN_0_88  = const(0)
HMC5883_GAIN_1_3   = const(1)
HMC5883_GAIN_1_9   = const(2)
HMC5883_GAIN_2_5   = const(3)
HMC5883_GAIN_4_0   = const(4)
HMC5883_GAIN_4_7   = const(5)
HMC5883_GAIN_5_6   = const(6)
HMC5883_GAIN_8_1   = const(7)

HMC5883_gain = {
    HMC5883_GAIN_0_88  : 1370,
    HMC5883_GAIN_1_3   : 1090,
    HMC5883_GAIN_1_9   : 820,
    HMC5883_GAIN_2_5   : 660,
    HMC5883_GAIN_4_0   : 440,
    HMC5883_GAIN_4_7   : 390,
    HMC5883_GAIN_5_6   : 330,
    HMC5883_GAIN_8_1   : 230}

# Mode register
HMC5883_MR_POS     = const(1)
HMC5883_MR_SIZE    = const(2)

HMC5883_mode = {
    0: "Continuous",
    1: "Single Measurement",
    2: "Idle",
    3: "Idle"}

HMC5883_MR_CONT     = const(0)
HMC5883_MR_SINGLE   = const(1) # default
HMC5883_MR_IDLE     = const(1) 

# Status register
HMC5883_STS_RDY     = const(0)
HMC5883_STS_LOCK    = const(1)

