#!/usr/bin/python3
import socket
import matplotlib.pyplot as plt
from collections import deque

def parse(msg):
    par_names = []
    par_values = []
    measParts = msg.split(",")
    print(measParts)
    for i in range(len(measParts)):
        tmp = measParts[i].split(":")
        par_names.append(tmp[0])
        try:
            val = float(tmp[1])
            par_values.append(val)
        except:
            print("measage " + msg + "does not have the required form")
            return None,None
        
    print(par_names)
    print(par_values)
    return par_names,par_values

def plot(msg):
    names,values = parse(msg)
    if not names:
        return
    # check if the queues have already been created
    # create them if not
    if len(queues) == 0:
        for i in range(len(names)):
            queues.append(deque(maxlen=100))
    # clear the plot
    plt.clf()
    for i in range(len(names)):
        queues[i].append(values[i])   # add the value to the ring buffer
        # plot the points
        plt.plot(queues[i],label=names[i])
        plt.scatter(range(len(queues[i])),queues[i])
    
    title = ""
    for i in range(len(names)):
        title += names[i] +" "
    plt.title(title)
    plt.legend(loc="upper left")
    plt.draw()
    plt.pause(0.01)
    
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def server_program():
    # get the hostname
    host = socket.gethostname()
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind(('', port))  # bind host address and port together

    print("Server running on " + host + " with IP: " + get_ip())
    print("Listening to any machine on port ",port)
    
    # configure to how many clients the server can listen simultaneously
    server_socket.listen(1)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    conn.send(("From server: Connected to " + get_ip()).encode())
    
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        if not data:
            # if data is not received break
            break
        print(str(data))
        plot(str(data))

    conn.close()  # close the connection
    
if __name__ == '__main__':
    queues = []
    server_program()
