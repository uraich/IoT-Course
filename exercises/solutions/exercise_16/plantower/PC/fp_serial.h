/* ====================================================================== */
/* Serial communication include file for fingerprint program              */
/* Copyright U. Raich March 2019                                          */
/* This code is released under GPL                                        */
/* It is part of a project for the course on embedded systems at the      */
/* University of Cape Coast, Ghana                                        */
/* ====================================================================== */
#ifndef __FP_SERIAL_H__
#define __FP_SERIAL_H__

#define FP_SUCCESS                     0
#define FP_BAD_OPEN                   -1
#define FP_ILLEGAL_BAUDRATE           -2
#define FP_ILLEGAL_PORT               -3
#define FP_WRITE_ERROR                -4
#define FP_READ_ERROR                 -5
#define FP_READ_TIMEOUT               -6

#define BAUDRATE                   57600

/**
* open_serial function
* @param[out] file descriptor
* @param[in] port number (0..3)
* @param[in] baud rate
* @param[out] error code
*/
void open_serial(int *handle, int *port, int *baudrate, int *errCode);
/**
* close_serial function
* @param[in] file descriptor
* @param[out] error code
*/
void close_serial(int *handle, int *errCode);
void write_serial(int *handle, char *str, int *size, int *errCode);
void read_serial(int *handle,char *buf, int *size, int *errCode);
void read_data_serial(int *handle,char *buf, int *size, int *errCode);
void status_serial(int *handle,char *errCode, int *nbread, int *nbwrite);

#endif /* __FP_SERIAL_H__ */

