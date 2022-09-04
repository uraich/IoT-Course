#!/usr/bin/python3
import sys,socket

def client_program(host_ip):
    host = socket.gethostname()  # as both code is running on same pc
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


if __name__ == '__main__':
    # check if IP address has been given
    if len(sys.argv) != 2:
        print("Usage: client_withIP IP_address_of_your_server")
        print("e.g. client_withIP 192.168.0.46")
        sys.exit()
    
    client_program(sys.argv[1])
