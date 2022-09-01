# station.py: Access WiFi through a station interface
#
# Copyright (c) U.Raich 28. Aug 2022
# The program is released under the MIT license
# It is part of the course on the Internet of Things at the
# University of Cape Coast, Ghana

import network
from utime import sleep_ms
import sys

ssid     = "SFR-3910_EXT"
password =  "Q7JYRGPJLYGZ"

sta_if = network.WLAN(network.STA_IF)
#
# check if the network is active and activate it, if not
#
if sta_if.active():
    print("Network interface is active")
else:
    print("Network interface is inactive, activating it...")
    sta_if.active(True)
    timeout=0
    for _ in range(500):   # timeout of 1s
        if sta_if.active():
            break;
        else:
            sleep_ms(10)
            timeout += 1
    if not sta_if.active():
        print("Problem activating the network interface")
        sys.exit()
    else:
        print("Network interface has been successfully activated")
        
#
# Scan for all available SSIDs
#

visible_ssids = sta_if.scan()
# sort the list on decreasing power
visible_ssids.sort(key=lambda x: x[3], reverse=True)

# print(visible_ssids)
print("Visible SSIDs are:")
print("   SSID\t\t\tBSSID\t\t\tchannel\tRSSI\tsecurity\tHidden")
for ssid_index in range(len(visible_ssids)):
    print(visible_ssids[ssid_index][0].decode() +"\t" ,end=" ")
    bssid = visible_ssids[ssid_index][1]

    for i in range(len(bssid)-1):
        print("0x{:02x},".format(bssid[i]),end="")
    print("0x{:02x}\t".format(bssid[i]),end="")
    channel  = visible_ssids[ssid_index][2]
    rssi     = visible_ssids[ssid_index][3]
    security = visible_ssids[ssid_index][4]
    hidden   = visible_ssids[ssid_index][5]
    #print(channel,rssi)
    print("   {:d}\t{:d}\t   {:d}\t\t  ".format(channel,rssi,security),end="")
    if hidden:
        print("Yes")
    else:
        print("No")
#
# Connect to the network
#

sta_if.connect(ssid,password)
print("Connecting ...")
timeout = 0
for _ in range(1000):
    if sta_if.isconnected():
        break
    else:
        timeout += 1
        sleep_ms(10)

if not sta_if.isconnected():
    print("WiFi connection failed. Please check your ssid and and password and make sure your router is visible")
    sys.exit()

else:
    print("ESP32 is connected to IP :",sta_if.ifconfig()[0])
#
# set the mDNS hostname
#
sta_if.config(dhcp_hostname="esp32Uli")
mac = sta_if.config("mac")
print("Its MAC address is: ",end="")
for i in range(len(mac)-1):
    print("{:02x}:".format(mac[i]),end="")
print("{:02x}".format(mac[i]))

# host = sta_if.config('dhcp_hostname')
# print("Hostname has been set, you can now access the ESP32 with: " + host + ".local")

