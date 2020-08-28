import uasyncio as asyncio
import as_GPS
from machine import UART

def callback(gps, *_):  # Runs for each valid fix
    print("GPS latitude: {}, GPS longitude: {}, altitude: {:f}".format(gps.latitude_string(), gps.longitude_string(), gps.altitude))
    print("Date and time: ",gps.date_string(formatting=as_GPS.LONG)," ",gps.time_string()," CET")
    print("Speed: ",gps.speed_string())
    print("no of satellites in view: {:d}".format(gps.satellites_in_view))

uart = UART(2, baudrate=115200, rx=21, tx=22, timeout=10000)
sreader = asyncio.StreamReader(uart)  # Create a StreamReader
gps = as_GPS.AS_GPS(sreader, fix_cb=callback, cb_mask = as_GPS.GLL | as_GPS.VTG | as_GPS.RMC, local_offset=2)  # Instantiate GPS

async def test():
    print('waiting for GPS data')
    await gps.data_received(position=True, date=True, altitude=True)
    await asyncio.sleep(60)  # Run for one minute
    
    print("Error statistics:")
    print("crc errors: {:d}".format(gps.crc_fails))
    print("no of clean sentences: {:d}".format(gps.clean_sentences))
    print("no of parsed sentences: {:d}".format(gps.parsed_sentences))
    print("no of unsupported sentences: {:d}".format(gps.unsupported_sentences))
    
loop = asyncio.get_event_loop()
loop.run_until_complete(test())
