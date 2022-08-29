/* read a wav file and print the header information */
/* copyright U. Raich February 2021                 */
/* This program is part of the course on IoT        */
/* at the University of Cape Coast (UCC), Ghana     */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HEADER_LENGTH 44

  typedef struct __attribute__((packed)) {
    char  riff[4];
    int   fileSize;
    char  wave[4];
    char  fmt[4];
    int   fmtDataLength;
    short fmtType;
    short noOfChannels;
    int   sampleRate;
    int   totalRate;
    short bitsPerSampleTimesChannel;
    short bitsPerSample;
    char  data[4];
    int   dataSize;
  } waveHeader;


int main(int argc, char *argv[]) {
  FILE * wavFile;
  int charsRead;
  char charBuf[5];
  waveHeader header;
   
  if (argc != 2) {
    printf("Usage %s wavFile\n",argv[0]);
    exit(-1);
  }

  printf("size of waveHeader: %ld\n",sizeof(waveHeader));
  wavFile = fopen(argv[1],"r");
  if ((charsRead = fread(&header,1,HEADER_LENGTH,wavFile)) != HEADER_LENGTH) {
    printf("Could not read the wav header\n");
    printf("Read %d chars\n",charsRead);
  }

  fclose(wavFile);
  charBuf[4]='\0';
  /*
    print header information
  */
  memcpy(charBuf,header.riff,4);
  printf("riff: %s\n",charBuf);
  printf("File size: 0x%0x = %d bytes\n",header.fileSize,header.fileSize);
  memcpy(charBuf,header.wave,4);
  printf("wave: %s\n",charBuf);
  memcpy(charBuf,header.fmt,4);
  printf("fmt: %s\n",charBuf);
  printf("Length of format data: %d\n",header.fmtDataLength);
  printf("Format type (1 is PCM) %d\n",header.fmtType);
  printf("Number of channels: %d\n",header.noOfChannels);
  printf("Sample rate: %d\n",header.sampleRate);
  printf("(Sample Rate * BitsPerSample * Channels) / 8: %d\n",header.totalRate);
  printf("(BitsPerSample * Channels) / 8.1 - 8 bit mono2 - 8 bit stereo/16 bit mono4 - 16 bit stereo: %d\n",
	 header.bitsPerSampleTimesChannel);
  printf("Bits per sample: %d\n",header.bitsPerSample);
  memcpy(charBuf,header.data,4);
  printf("data: %s\n",charBuf);
  printf("Size of the data section: %d\n",header.dataSize);
  
}
