import network
import sys,socket
import time
import dht
from machine import Pin
ssid     = "SFR-3910"
password = "Q7JYRGPJLYGZ"
# ssid     = "WLAN18074253"
# password =  "Q4k6V35sFauw"

def client_program(host_ip):
    port = 5000  # socket server port number
    print("Reading temperature and humidity from DHT11 on pin {:d}".format(
        _DHT11_PIN))
    client_socket = socket.socket()  # instantiate
    print("Connecting to ",host_ip ," on port :",port)
    try:
        client_socket.connect((host_ip, port))  # connect to the server
    except OSError as error:
        print("Connection failed, please check IP address and port number")
        sys.exit()
        
    data = client_socket.recv(1024).decode()  # receive response
    print(data)
    
    while True:
        dht11.measure()
        temperature = dht11.temperature()
        relHumidity = dht11.humidity()
        message = "Temperature [°C]: {:d},Humidity [%]: {:d}".format(
            temperature,relHumidity)

        try:
            client_socket.send((message + '\r\n').encode())  # send message
            time.sleep(1)
        except:
            if not station.isconnected():
                print("Trying to re-connect to WiFi")
                station.active(False)
                time.sleep_ms(50)
                station.activate(True)
                station.connect(ssid, password)
                while not station.isconnected():
                    pass

# define dht11 interface
_DHT11_PIN = 22
dht11 = dht.DHT11(Pin(_DHT11_PIN))

# connect to wifi
station = network.WLAN(network.STA_IF)
if station.isconnected() == True:
    print("Already connected")
if station.active():
    print("Station is already active")
else:
    print ("Activating station")
    if not station.active(True):
        print("Cannot activate station! giving up ...")
        sys.exit()
ssids = station.scan()
for i in range(len(ssids)):
    print(ssids[i][0],end=" ")
print("")
station.connect(ssid, password)
while not station.isconnected():
    pass
print("Connection successful, IP: " + station.ifconfig()[0])

# host IP is 192.168.0.14
host_ip = "192.168.0.14"
client_program(host_ip)
