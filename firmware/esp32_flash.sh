#!/bin/sh
# flashes the esp32 camera board with MicroPython
# written by U. Raich for the AIS conference 2020 Kinshasa
# make sure GPIO-0 is connected to ground through a jumper
esptool -b 460800 write_flash --flash_size=detect --flash_mode dio 0x1000 firmware.bin
