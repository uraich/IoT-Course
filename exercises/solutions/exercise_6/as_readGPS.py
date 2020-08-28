# reads the number of sentences specified by sentencecount
# and prints them out
# The sentences can be saved in a file and parsed by as_GPS_parse.py
# Copyright U. Raich August 2020
# This program is part of the course on IoT at the University of Cape Coast, Ghana
# It is released under GPL

import uasyncio as asyncio
import as_GPS as as_GPS
from machine import UART

uart = UART(2, baudrate=115200, rx=21, tx=22, timeout=10000)
sreader = asyncio.StreamReader(uart)  # Create a StreamReader

async def test():
    sentence_count = 0
    while sentence_count < 400:
        line = await sreader.readline()
        try:
            line=line.decode('utf8')
        except:
            continue
        line.strip()
        if line[0] != '$':
            continue
        if not '*' in line:
            continue
        print(line,end="")
        sentence_count += 1

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
