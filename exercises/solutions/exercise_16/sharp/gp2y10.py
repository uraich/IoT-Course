# Dust Sensor Sharp GP2Y1010AU0F
######################
# 1 blue LED R 150 Ohm
# 2 green LED Ground
# 3 white LED D8: GPIO 5
# 4 yellow Ground
# 5 black V0  measure Pin 32
# 6 red Vcc 5V
######################

from machine import Pin, ADC
from utime import sleep, sleep_us
measurePIN = ADC(Pin(36))
measurePIN.atten(ADC.ATTN_11DB) #range 0-4095 -> 3,3 V
LedPower = Pin(5,Pin.OUT)
samplingTime = 280 #original 280
deltaTime = 40
sleepTime = 9680
voMeasured = 0
calcVoltage = 0
dustDensity = 0
print('***************** START *************************')

while True:
    LedPower.off()
    sleep_us(samplingTime)
    voMeasured = measurePIN.read() # read Dust Value
    sleep_us(deltaTime)
    LedPower.on()
    sleep_us(sleepTime)

    print('***************** 1111111 *************************')

    # 0 – 3,3 V mapped to 0 – 4095
    calcVoltage = voMeasured * (3.3 / 4096.0)
    if calcVoltage > 3.5:
        print("Sensor is saturating")
    # dustDensity = 0.17 * calcVoltage – 0.01
    dustDensity = 0.17 * calcVoltage - 0.01
    print('Raw Signal Value (0-4095): {0:3.2f}'.format(voMeasured))
    print(' – Voltage: {0:3.2f} V'.format(calcVoltage))
    print(' – Dust Density: {0:3.2f} mg/m3'.format(dustDensity))
    
    sleep(1)

print('***************** END **************************')
