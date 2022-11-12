from wifi_connect import connect
connect()
import uasyncio as asyncio
 
async def echo_server(reader, writer):
    while True:
        data = await reader.read(100)  # Max number of bytes to read
        if not data:
            break
        writer.write(data)
        await writer.drain()  # Flow control, see later
    writer.close()

async  def main(host, port):
    server = await asyncio.start_server(echo_server, host, port)
    server.wait_closed()

asyncio.run(main('', 5000))
print("Please connect to http://"+getIPAddress())
evt_loop = asyncio.get_event_loop()
evt_loop.run_forever()
