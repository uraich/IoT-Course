import network
import sys,socket
import time
from wifi_connect import connect

def client_program(host_ip):
    host = "ESP32"  
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    print("Connecting to ",host,":",port)
    try:
        client_socket.connect((host_ip, port))  # connect to the server
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

# connect to wifi
connect()
# host IP is 192.168.0.14
host_ip = "192.168.0.14"
client_program(host_ip)
