from micropython import const
ADXL345_ADDRESS               = const(0x53)    # I2C address of adxl345
ADXL345_DEVICE_ID             = const(0xe5)    # 

ADXL345_DEVID                 = const(0x00)    # Device ID
ADXL345_THESH_TAP             = const(0x1d)    # Tap threshold
ADXL345_OFSX                  = const(0x1e)    # X-axis offset
ADXL345_OFSY                  = const(0x1f)    # y-axis offset
ADXL345_OFSZ                  = const(0x20)    # z-axis offset
ADXL345_DUR                   = const(0x21)    # Tap duration
ADXL345_LATENT                = const(0x22)    # Tap latency
ADXL345_WINDOW                = const(0x23)    # Tap window
ADXL345_THRESH_ACT            = const(0x24)    # Activity threshold
ADXL345_THRESH_INACT          = const(0x25)    # Inactivity threshold
ADXL345_TIME_INACT            = const(0x26)    # Inactivity time
ADXL345_ACT_INACT_CTL         = const(0x27)    # Axis enable for activity and inactivity detection
ADXL345_THRESH_FF             = const(0x28)    # Free-fall threshold
ADXL345_TIME_FF               = const(0x29)    # Free-fall time
ADXL345_TAP_AXIS              = const(0x2a)    # Axis control for single/touble tap
ADXL345_ACT_TAP_STATUS        = const(0x2b)    # Source of single/touble tap
ADXL345_BW_RATE               = const(0x2c)    # Data rate and power mode control
ADXL345_POWER_CTL             = const(0x2d)    # Power-saving features control
ADXL345_INT_ENABLE            = const(0x2e)    # Interrupt enable control
ADXL345_INT_MAP               = const(0x2f)    # Interrupt mapping control
ADXL345_INT_SOURCE            = const(0x30)    # Source of Interrupts
ADXL345_DATA_FORMAT           = const(0x31)    # Data format control
ADXL345_DATAAX0               = const(0x32)    # X-Axis Data 0
ADXL345_DATAAX1               = const(0x33)    # X-Axis Data 1
ADXL345_DATAAY0               = const(0x34)    # Y-Axis Data 0
ADXL345_DATAAY1               = const(0x35)    # Y-Axis Data 1
ADXL345_DATAAZ0               = const(0x36)    # Z-Axis Data 0
ADXL345_DATAAZ1               = const(0x37)    # Z-Axis Data 1
ADXL345_FIFO_CTL              = const(0x38)    # FIFO control
ADXL345_FIFO_STATUS           = const(0x39)    # FIFO status

# Bit definitions

# ACT_INACT_CTL
INACT_Z_EN                    = const(0)
INACT_Y_EN                    = const(1)
INACT_X_EN                    = const(2)
INACT_AC_DC                   = const(3)
ACT_Z_EN                      = const(4)
ACT_Y_EN                      = const(5)
ACT_X_EN                      = const(6)
ACT_AC_DC                     = const(7)

# TAP AXES
TAP_X_EN                      = const(0)
TAP_Y_EN                      = const(1)
TAP_Z_EN                      = const(2)
SUPPRESS                      = const(3)

# ACT_TAP_STATUS 
TAP_Z_SOURCE                  = const(0)
TAP_Y_SOURCE                  = const(1)
TAP_X_SOURCE                  = const(2)
ASLEEP                        = const(3)
ACT_Z_SOURCE                  = const(4)
ACT_Y_SOURCE                  = const(5)
ACT_X_SOURCE                  = const(6)

# BW_RATE
RATE                          = const(3)
RATE_SIZE                     = const(4)
LOW_POWER                     = const(4)
LOW_POWER_SIZE                = const(2)

# POWER_CTL
WAKEUP                        = const(1)
WAKEUP_SIZE                   = const(2)
SLEEP                         = const(2)
MEASURE                       = const(3)
AUTO_SLEEP                    = const(5)
AUTO_SLEEP_SIZE               = const(2)
LINK                          = const(5)

# INT_ENABLE
OVERRUN                       = const(0)
WATERMARK                     = const(1)
FREE_FALL                     = const(2)
INACTIVITY                    = const(3)
ACTIVITY                      = const(4)
DOUBLE_TAP                    = const(5)
SINGLE_TAP                    = const(6)
DATA_READY                    = const(7)

# DATA_FORMAT
RANGE                         = const(1)
RANGE_SIZE                    = const(2)
JUSTIFY                       = const(2)
FULL_RES                      = const(3)
FULL_RES_SIZE                 = const(2)
INT_INVERT                    = const(5)
SPI                           = const(6)
SELF_TEST                     = const(7)

# FIFO_CTL
SAMPLES                       = const(4)
SAMPLES_SIZE                  = const(5)
TRIGGER                       = const(5)
FIFO_TYPE                     = const(7)
FIFO_TYPE_SIZE                = const(2)

# FIFO_STATUS
FIFO_ENTRIES                  = const(5)
FIFO_ENTRIES_SIZE             = const(6)
FIFO_TRIG                     = const(7)

# Data rates
RATE_3200                     = const(0xf)
RATE_1600                     = const(0xe)
RATE_800                      = const(0xd)
RATE_400                      = const(0xc)
RATE_200                      = const(0xb)
RATE_100                      = const(0xa)
RATE_50                       = const(0x9)
RATE_25                       = const(0x8)
RATE_12_5                     = const(0x7)
RATE_6_25                     = const(0x6)
RATE_3_13                     = const(0x5)
RATE_0_78                     = const(0x4)
RATE_0_39                     = const(0x3)
RATE_0_20                     = const(0x1)
RATE_0_10                     = const(0x0)

# Acceleration full range
ACCEL_2G                      = const(0)
ACCEL_4G                      = const(1)
ACCEL_8G                      = const(2)
ACCEL_16G                     = const(3)

# FIFO
BYPASS                        = const(0)
FIFO_MODE                     = const(1)
STREAM_MODE                   = const(2)
TRIGGER_MODE                  = const(3)

# POWER_CTL Wakeup frequency
WAKE_UP_8_HZ                  = const(0)
WAKE_UP_4_HZ                  = const(1)
WAKE_UP_2_HZ                  = const(2)
WAKE_UP_1_HZ                  = const(3)

