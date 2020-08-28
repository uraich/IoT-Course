#
# send data to the second UART
# it is connected to
# Rx: GPIO 17
# Tx: GPIO 16


import machine
u2=machine.UART(2, baudrate=115200, rx=21, tx=22, timeout=10000)

while True:
    try:
        line = u2.readline().decode('utf8')
        line = line.rstrip()
        print(line)
    except:
        pass
