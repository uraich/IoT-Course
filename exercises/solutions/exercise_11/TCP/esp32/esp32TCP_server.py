import network
import socket
import time
from wifi_connect import connect,getIPAddress

port           =   5000                 #input the remote port

# connect to wifi
connect()
ip = getIPAddress()
          
# The server code
server_socket = socket.socket()  # get instance
# look closely. The bind() function takes tuple as argument
server_socket.bind(('', port))  # bind host address and port together

# configure how many client the server can listen simultaneously
print("Listening to any machine on IP: ",getIPAddress()," port ",port)    
server_socket.listen(1)
conn, address = server_socket.accept()  # accept new connection
print("From server: Connection from: " + str(address))
conn.send("Connected to " + ip)

while True:
  # receive data stream. it won't accept data packets greater than 1024 bytes
  data = conn.recv(1024).decode()
  if not data:
    # if data is not received break
    break
  print("from connected user: " + str(data))
  data = input(' -> ')
  conn.send(data.encode())  # send data to the client
  
conn.close()  # close the connection
