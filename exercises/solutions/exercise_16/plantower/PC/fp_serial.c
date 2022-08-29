/*
 * Serial driver for fingerprint module
 * copyright U. Raich, Dec 2018
 */
#include <sys/types.h>
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

#include "fp_serial.h"
#include "fp.h"

extern bool debug;
struct termios oldtio,newtio;
int noOfCharsRead,noOfCharsWritten;
int correctHandle;

void open_serial(int *handle,int *port, int *baudrate, int *errCode){
  int fd;
  tcflag_t br;
  char modemDevice[15];

  if ((*port < 0) || (*port > 3)) {
    *errCode = FP_ILLEGAL_PORT;
    return;
  }
  sprintf(modemDevice,"/dev/ttyUSB%d",*port);
  if (debug)
    printf("open_serial: modem device: %s\n",modemDevice);

  switch (*baudrate) {
  case 9600:
    br = B9600;
    break;
  case 19200:
    br = B19200;
    break;
  case 38400:
    br = B38400;
    break;
  case 57600:
    br = B57600;
    break;
  case 115200:
    printf("Setting baudrate to 115200 baud\n");
    br = B115200;
    break;
  default:
    fprintf(stderr,"open_serial: Illegal baud rate\n");
    *errCode = FP_ILLEGAL_BAUDRATE;
    return;
  }
  fd = open(modemDevice, O_RDWR | O_NOCTTY ); 
  if (fd <0) {
    fprintf(stderr,"open_serial: error when trying to open serial line %s\n",
        modemDevice);
    *errCode = FP_BAD_OPEN;
    return;
  }
  else {
    *handle = fd;
    correctHandle=fd;
    if (debug)
      printf("Handle is %d\n",fd);
    //    sleep(2);
  }
    
  if (debug)
    printf("open_serial: Serial port successfully opened with handle: %d\n",fd);

  /*
    set the baud rate
  */
  
  // Initialize file descriptor sets
  fd_set read_fds, write_fds, except_fds;
  FD_ZERO(&read_fds);
  FD_ZERO(&write_fds);
  FD_ZERO(&except_fds);
  FD_SET(fd, &read_fds);

  tcgetattr(fd,&oldtio); /* save current port settings */

  bzero(&newtio, sizeof(newtio));
  newtio.c_cflag = br | CRTSCTS | CS8 | CLOCAL | CREAD;
  newtio.c_iflag = IGNPAR;
  newtio.c_oflag = 0;
  
  /* set input mode (non-canonical, no echo,...) */
  newtio.c_lflag = 0;
   
  newtio.c_cc[VTIME]    = 0;   /* inter-character timer unused */
  newtio.c_cc[VMIN]     = 2;   /* blocking read until 5 chars received */
  
  tcflush(fd, TCIFLUSH);
  tcsetattr(fd,TCSANOW,&newtio);
  noOfCharsRead = noOfCharsWritten = 0;
  sleep(2);
  *errCode = FP_SUCCESS;
  return;
}

void close_serial(int *handle, int *errCode) {

  if (*handle != correctHandle) {
    fprintf(stderr,"The serial port wass not correctly opened, cannot close it\n");
    *errCode = FP_BAD_OPEN;
    return;
  }
  if (debug)
    printf("close_serial: resetting serial line pars and closing\n");
  tcsetattr(*handle,TCSANOW,&oldtio);
  close(*handle);
  return;
}

void write_serial(int *handle, char *str, int *size, int *errCode) {
  int i;
  if (*handle != correctHandle) {
    fprintf(stderr,"The serial port wass not correctly opened, cannot close it\n");
    *errCode = FP_BAD_OPEN;
    return;
  }

  if ((noOfCharsWritten = write(*handle, str, *size)) != *size) {
    printf("Write error\n");
    *errCode = FP_WRITE_ERROR;
  }
  else {
    if (debug) {
    printf("write_serial: wrote %d bytes to serial port\n",*size);
    printf("The text was:\n");
    for (i=0; i<*size; i++) {
      printf("0x%02x ",(uint8_t)str[i]);
      if (!((i+1)%16))
	printf("\n");
    }
    printf("\n");
    }
  }
  return;
}


void read_serial(int *handle, char *buf, int *size, int *errCode) {

  int fd=*handle;
  int i,bytesRead=0;
  int retCode;
  struct timeval timeout;
  if (debug)
    printf("read_serial: handle is %d\n",fd);

  timeout.tv_sec =  5;
  timeout.tv_usec = 0;
  
  if (*handle != correctHandle) {
    fprintf(stderr,"The serial port wass not correctly opened, cannot close it\n");
    *errCode = FP_BAD_OPEN;
    return;
  }

  // Initialize file descriptor sets
  fd_set read_fds, write_fds, except_fds;
  FD_ZERO(&read_fds);
  FD_ZERO(&write_fds);
  FD_ZERO(&except_fds);
  FD_SET(fd, &read_fds);
  usleep(50000);
  
  retCode = select(fd+1,&read_fds,&write_fds,&except_fds,&timeout);
  if (retCode > 0) {
    if ((bytesRead=read(fd,buf,*size)) != *size) {
      usleep(100000);
      bytesRead += read(fd,buf+bytesRead,*size-bytesRead);
      if (debug)
	printf("Read at second try: %d\n", bytesRead);
    }
    
    if (debug) {
      printf("Read from serial port: ");
      for (i=0; i<*size;i++)
	printf("0x%02x ",(uint8_t)buf[i]);
      printf("\n");
     }
    *errCode = FP_SUCCESS;
  }
  else if (retCode == 0) {
    printf("Timeout on reading\n");
    *errCode = FP_READ_TIMEOUT;
  }
  else {
    printf("Error on reading\n");
    *errCode = FP_READ_ERROR;
  }
}

void status_serial(int *handle,char *errCode, int *nbread, int *nbwrite) {
  *nbread = noOfCharsRead;
  *nbwrite = noOfCharsWritten;
  *errCode = FP_SUCCESS;
}
