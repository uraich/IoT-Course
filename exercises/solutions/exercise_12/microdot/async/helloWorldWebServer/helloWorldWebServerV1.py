# The simplest possible WEB server printing "Hello World!"
# Program written for the IoT course at the University of Cape Coast
# This first version does not use picoweb but accesses the socket interface
# directly
# copyright (c) U. Raich November 2022
# This program is released under GPL

import uasyncio as asyncio

from wifi_connect import connect, getIPAddress
import uerrno

print ("Connecting to the network")
connect()

html = """ <!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>
<title>Hello World </title>
<h1>The Hello World! HTML page</h1>
<p>This is the Hello World html page Version 1, served by a WEB server communicating through sockets directly.<br>
  The html code is embedded in the server itself. There is no separate HTML file. <br>
  The program was written for<br>
  the <b>Course on the Internet of Things (IoT) </b>at the
  University of Cape Coast (Ghana) <br>
  Copyright (c) U. Raich, November 2022, <br>released under GPL
  
</p>
<p><a href="/shutdown">Click to shutdown the server</a></p>
</body>
</html> 
"""

async def webserver(reader,writer):
    while True:
        request = await reader.read(100)
        request_components = request.decode().split(" ")
        print("Request components:")
        for i in range(len(request_components)):
            print(request_components[i])
                       
        if b'GET' in request:
            if request_components[1] == '/':
                print("Request: ",request)
                writer.write("HTTP/1.0 200 OK\r\n")
                writer.write("Content-Type: text/html\r\n")
                writer.write("\r\n")
                writer.write(html)
                await writer.drain()
            elif request_components[1] == '/shutdown':
                print("Shutdown server")
                writer.close()
                await writer.wait_closed()
                return
            else:
                writer.write("HTTP/1.0 404 \r\n")
                writer.write("Content-Type: text/html\r\n")
                writer.write("\r\n")
                await write.drain()
                
    
async  def main(host, port):
    print("Please connect to http://"+getIPAddress())
    server = await asyncio.start_server(webserver, host, port)
    
asyncio.run(main('', 80))
evt_loop = asyncio.get_event_loop()
evt_loop.run_forever()
