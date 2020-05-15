#!/bin/sh
# erases flash of esp32 camera board
# written by U. Raich for the AIS conference 2020 Kinshasa
# make sure GPIO-0 is connected to ground through a jumper
esptool erase_flash
