# tcpClient.py: a test TCP client
# The client connects to a tcp server on the PC and allows to send a few
# text messages
# copyright U. Raich 31.5.2022
# This program is released under the MIT license

import sys
import usocket as socket
from wifi_connect import *
SERVER_IP = '192.168.0.13'     # please check this with ifconfig on the PC

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
    
    message = input(" -> ")  # take input

    while message.lower().strip() != 'bye':
        client_socket.send((message + '\r\n').encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response

        print('Received from server: ' + data)  # show in terminal

        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection
    
# connect to WiFi
connect()
client_program(SERVER_IP)
