/*
 * read the plantower dust sensor
 * copyright (c) U. Raich, 21.June 2020
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "fp_serial.h"

#define PMS5003_MSG_LENGTH 32
#define MAGIC 0x424d
bool debug=false;

int main(int argc, char **argv) {
  int i,retCode;
  int handle;
  int port=0;
  int baudrate=9600;
  uint8_t msgBuf[PMS5003_MSG_LENGTH];
  int msgBufLength=PMS5003_MSG_LENGTH;
  uint16_t framelength;
  uint16_t tmp;
  uint16_t chksum;  
  /* open serial port */
  open_serial(&handle,&port,&baudrate,&retCode);
  if (retCode == FP_SUCCESS)
    printf("Plantower PM5003 serial connection successfully opened\n");
  else
    return -1;

  while (true) {
    /* read a message */
    read_serial(&handle,(char *)msgBuf,&msgBufLength,&retCode);
    if (retCode == FP_SUCCESS) {
      for (i=0;i<PMS5003_MSG_LENGTH;i++)
	printf("%02x ",msgBuf[i]);
    }
    printf("\n");
    /* check the start characters */
    if (((msgBuf[0] << 8) | msgBuf[1]) != MAGIC) {
      printf("Incorrect Plantower message header\n");
      close_serial(&handle,&retCode);
      return -1;
    }
    framelength= (msgBuf[2] << 8) | msgBuf[3];
    printf("Frame length: %d\n",framelength);
    
    /* calculate checksum */
    chksum=0;
    for (i=0;i<PMS5003_MSG_LENGTH-2;i++)
      chksum += msgBuf[i];
    if (chksum != ((msgBuf[PMS5003_MSG_LENGTH-2] << 8) | msgBuf[PMS5003_MSG_LENGTH-1])) {
      printf("Wrong checksum\n");
    }
    else {
      /* read out the data and print the results */
      /* data 1 */
      tmp = (msgBuf[4] << 8) | msgBuf[5];
      printf("PM1.0 concentration [ug/m3] (CF=1, standard particle): %d\n",tmp);
      /* data 2 */
      tmp = (msgBuf[6] << 8) | msgBuf[7];
      printf("PM2.5 concentration [ug/m3] (CF=1, standard particle): %d\n",tmp);
      /* data 3 */
      tmp = (msgBuf[8] << 8) | msgBuf[9];
      printf("PM10 concentration [ug/m3]: (CF=1, standard particle): %d\n",tmp);
      /* data 4 */
      tmp = (msgBuf[10] << 8) | msgBuf[11];
      printf("PM1.0 concentration [ug/m3]: (under atmospheric environment): %d\n",tmp);
      /* data 5 */
      tmp = (msgBuf[12] << 8) | msgBuf[13];
      printf("PM2.5 concentration [ug/m3]: (under atmospheric environment): %d\n",tmp);
      /* data 6 */
      tmp = (msgBuf[14] << 8) | msgBuf[15];
      printf("Concentration unit: (under atmospheric environment): %d\n",tmp);
      /* data 7 */
      tmp = (msgBuf[16] << 8) | msgBuf[17];
      printf("Number of particles with diameter beyond 0.3 um in 0.1L of air: %d\n",tmp);
      /* data 8 */
      tmp = (msgBuf[18] << 8) | msgBuf[19];
      printf("Number of particles with diameter beyond 0.5 um in 0.1L of air: %d\n",tmp);
      /* data 9 */
      tmp = (msgBuf[20] << 8) | msgBuf[21];
      printf("Number of particles with diameter beyond 1.0 um in 0.1L of air: %d\n",tmp);
      /* data 10 */
      tmp = (msgBuf[22] << 8) | msgBuf[23];
      printf("Number of particles with diameter beyond 2.5 um in 0.1L of air: %d\n",tmp);
      /* data 11 */
      tmp = (msgBuf[24] << 8) | msgBuf[25];
      printf("Number of particles with diameter beyond 5.0 um in 0.1L of air: %d\n",tmp);
      /* data 12 */
      tmp = (msgBuf[24] << 8) | msgBuf[25];
      printf("Number of particles with diameter beyond 10.0 um in 0.1L of air: %d\n",tmp);      
    }
  }
  close_serial(&handle,&retCode);  
}
