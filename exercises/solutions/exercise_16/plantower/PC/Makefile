CFLAGS=-g -Wall
CC=gcc
all: plantower

fp_serial.o: fp_serial.c fp_serial.h fp.h

plantower: plantower.o fp_serial.o
	$(CC) $(CFLAGS) -o plantower plantower.o fp_serial.o
