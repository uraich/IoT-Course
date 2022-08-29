# accessPoint.py: Create a WiFi access point on the ESP32
#
# Copyright (c) U.Raich 28. Aug 2022
# The program is released under the MIT license
# It is part of the course on the Internet of Things at the
# University of Cape Coast, Ghana

import network
from utime import sleep_ms
import sys

ap_if = network.WLAN(network.AP_IF)
#
# check if the network is active and activate it, if not
#

if ap_if.active():
    print("Network interface is active")
else:
    print("Network interface is inactive, activating it...")
    ap_if.active(True)
    timeout=0
    for _ in range(100):   # timeout of 1s
        if ap_if.active():
            break;
        else:
            sleep_ms(10)
            timeout += 1
    if not ap_if.active():
        print("Problem activating the network interface")
        sys.exit()
    else:
        print("Network interface has been successfully activated")
        
print("Result of ap_if.ifconfig(): ",ap_if.ifconfig())
print("Connect the PC to this access point on IP",ap_if.ifconfig()[0],end=" ")
print("and check communication using ping")
