#!/usr/bin/python3
# vw_ server: vritual world test program
# The server waits for messages from the ESP32 transmitting color and distance
# information of the colored paper in front of the TCS3200 and HC-SR04 sensors

import socket
from vpython import * #import vPython library

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
        print("from connected user: " + str(data))

    conn.close()  # close the connection
    
if __name__ == '__main__':
    # create the scene
    # import the ultra-sonic ranger library
    scene=canvas(title='Virtual World with distance sensor') #Create your scene and give it a title.

    scene.width=800  #We can set the dimension of your visual box. 800X800 pixels works well on my screen
    scene.height= 600
    scene.autoscale=False #We want to set the range of the scene manually for better control. Turn autoscale off
    #scene.range = (12,12,12) #Set range of your scene to be 12 inches by 12 inches by 12 inches.
    
    target=box(length=.1, width=10,height=5, pos=vector(-2,0,0)) #Create the object that will represent your target (which is a colored card for our project)
    
    myBoxLED=box(color=color.blue,length=.1, width=5,height=5, pos=vector(-8.5,0,-12))
    myTubeLed1=cylinder(color=color.gray(1),pos=vector(-8.5,-1.8,-13.5), radius=0.5,length=1.0 )
    myTubeLed2=cylinder(color=color.gray(1),pos=vector(-8.5,1.8,-13.5), radius=0.5,length=1.0 )
    myTubeLed3=cylinder(color=color.gray(1),pos=vector(-8.5,-1.8,-10.5), radius=0.5,length=1.0 )
    myTubeLed4=cylinder(color=color.gray(1),pos=vector(-8.5,1.8,-10.5), radius=0.5,length=1.0 )
    myTubeLed5=cylinder(color=color.gray(0.1),pos=vector(-8.5,0,-12), radius=1.2,length=0.5 )
    #
    myBoxEnd=box(color=color.blue,length=.1, width=10,height=5, pos=vector(-8.5,0,0)) #This object is the little square that is the back of the ultrasonic sensor
    myTube2=cylinder(pos=vector(-8.5,0,-2.5), radius=1.5,length=2.0 ) #One of the 'tubes' in the front of the ultrasonic sensor
    myTube3=cylinder(pos=vector(-8.5,0,2.5), radius=1.5,length=2.0 )  #Other tube
    myTube4=cylinder(color=color.black, pos=vector(-6.6,0,2.5), radius=1.2,length=0.2 )
    myTube5=cylinder(color=color.black, pos=vector(-6.6,0,-2.5), radius=1.2,length=0.2 )
    myBoxQuartz=box(color=color.white,length=0.5, width=2, height=0.5, pos=vector(-8.2,2,0))
    
    myBall=sphere(color=color.red, radius=.3)
    
    lengthLabel = label(pos=vector(0,7,0), text='Target Distance is: ', box=False, height=20)


    server_program()
