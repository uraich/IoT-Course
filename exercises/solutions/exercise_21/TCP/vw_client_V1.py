# vw_client.py: Connects to the virtual world server (vw_server.py) on the PC
# Periodically sends data of color and distance information
# copyright U. Raich 31.5.2022
# This program is released under the MIT license

import sys
import usocket as socket
from utime import sleep_ms
from tcs3200 import TCS3200
from hc_sr04 import HC_SR04
from wifi_connect import *
SERVER_IP = '192.168.0.14'     # please check this with ifconfig on the PC

def client_program(host_ip):
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    print("Connecting to ",SERVER_IP,":",port)
    try:
        client_socket.connect((SERVER_IP, port))  # connect to the server
    except OSError as error:
        print("Connection failed, please check IP address and port number")
        sys.exit()
        
    data = client_socket.recv(1024).decode()  # receive response
    print(data)

    while True:
        try:
            # measure the distance
            echo_time = hc_sr04.measure()
            distance = hc_sr04.distance(echo_time)
            # acquire le color components
            rgb = tcs3200.rgb  # read the color of the paper
            
            message = "distance: {:f}, color: {:02d}, {:02d}, {:02d}".format(
                distance, rgb[0],rgb[1],rgb[2])
            # print(message)
            client_socket.send((message + '\r\n').encode())  # send message
            data = client_socket.recv(16).decode()           # wait for acknowledge
            # print("received from server: ",data)
            sleep_ms(50)
            
        except KeyboardInterrupt:
            client_socket.close()  # close the connection
            return
            
# connect to WiFi
connect()
# initialize the TCS3200 sensor
# create an TCS3200 object
tcs3200 = TCS3200(OUT=19, S2=5, S3=18, S0=17, S1=15, LED=23)
hc_sr04 =  HC_SR04()
# set debugging on
tcs3200.debugging=tcs3200.OFF

# switch the LEDs on
tcs3200.led = tcs3200.ON
# Set no of cycles to be measured
tcs3200.cycles=10
tcs3200.calibrate()
black_freq = tcs3200.calib(tcs3200.BLACK)
print("Calibration frequencies for black: ",black_freq)
white_freq = tcs3200.calib(tcs3200.WHITE)
print("Calibration frequencies for white: ",white_freq)

client_program(SERVER_IP)
