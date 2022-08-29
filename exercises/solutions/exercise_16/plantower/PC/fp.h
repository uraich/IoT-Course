/* include file for the FPM-10 finger print module            */
/* copyright U. Raich, March 2019                             */
/* This software is released under GPL                        */
/* It has been written for the course on embedded systems     */
/* at the University of Cape Coast, Ghana                     */

#ifndef __FP_H__
#define __FP_H__
#include "fp_serial.h"
#include <termios.h>
#include <stdbool.h>
#include <stdint.h>

#define FP_HEADER               0xef01
#define FP_HEADER_SIZE          2
#define FP_ADDRESS              0xffffffff
#define FP_ADDRESS_SIZE         4
#define FP_IDENTIFIER_SIZE      1
#define FP_LENGTH_SIZE          2
#define FP_CHECKSUM_SIZE        2
#define FP_PKT_HEADER_LENGTH    9
#define FP_BASE_PKT_SIZE       FP_HEADER_SIZE+FP_ADDRESS_SIZE+FP_IDENTIFIER_SIZE+FP_LENGTH_SIZE+FP_CHECKSUM_SIZE
#define FP_PAGE_SIZE           32
#define FP_NOTEPAD_SIZE        16
#define FP_DATA_PKT_LENGTH    128
#define FP_CONF_CODE_POS        9
#define FP_IDENTIFIER_POS       6
#define FP_MAX_TEMPLATES      150
#define FP_TEMPLATE_BLOCKS     12

#define FP_IMAGE_WIDTH        256
#define FP_IMAGE_HEIGHT       288
#define FP_CHARBUF_SIZE       512
#define FP_CMD_PACKET        0x01
#define FP_DATA_PACKET       0x02
#define FP_ACQ_PACKET        0x07
#define FP_END_PACKET        0x08
#define FP_BAUDRATE          0x04
#define FP_SECURITY          0x05
#define FP_PACKET_SIZE       0x06
#define FP_DEFAULT_BAUDRATE  0x06

/* error codes, these follow the ones on fp_serial.h */
#define FP_ILLEGAL_INSTRUCTION          -10
#define FP_INVALID_PACKET               -11
#define FP_BAD_CHECKSUM                 -12
#define FP_DANGEROUS                    -13
#define FP_ILLEGAL_CHARBUF              -14
#define FP_BMP_OPEN_ERROR               -20
#define FP_BMP_WRITE_ERROR              -21
#define FP_ILLEGAL_PARAMETER            -22

/* command codes */
#define FP_CMD_SET_PASSWORD            0x12
#define FP_CMD_VFY_PASSWORD            0x13
#define FP_CMD_HANDSHAKE               0x17
#define FP_CMD_SET_ADDR                0x15
#define FP_CMD_SET_SYS_PARA            0x0e
#define FP_CMD_READ_SYS_PARA           0x0f
#define FP_CMD_READ_CON_LIST           0x1f
#define FP_CMD_TEMPLATE_NUM            0x1d
#define FP_CMD_GEN_IMAGE               0x01
#define FP_CMD_UP_IMAGE                0x0a
#define FP_CMD_DOWN_IMAGE              0x0b
#define FP_CMD_IMG2TZ                  0x02
#define FP_CMD_REG_MODEL               0x05
#define FP_CMD_UP_CHAR                 0x08
#define FP_CMD_DOWN_CHAR               0x09
#define FP_CMD_STORE                   0x06
#define FP_CMD_LOAD                    0x07
#define FP_CMD_DEL_CHAR                0x0c
#define FP_CMD_EMPTY                   0x0d
#define FP_CMD_MATCH                   0x03
#define FP_CMD_SEARCH                  0x04
#define FP_CMD_RANDOM                  0x14
#define FP_CMD_WRITE_NOTEPAD           0x18
#define FP_CMD_READ_NOTEPAD            0x19

#define FP_CONFIRMATION_CODE_POS          9

/* return codes from fingerprint module */
#define CMD_EXECUTION_COMPLETE         0x00
#define ERR_RECEIVING_DATA_PACKAGE     0x01
#define ERR_NO_FINGER                  0x02
#define ERR_ENROLL                     0x04
#define ERR_BAD_IMAGE                  0x06
#define ERR_TOO_SMALL_IMAGE            0x07
#define ERR_PRINTS_DONT_MATCH          0X08
#define ERR_NO_MATCH                   0x09
#define ERR_COMBINE                    0x0a
#define ERR_ADDRESS_BEYOND_LIBRARY     0x0b
#define ERR_TEMPLATE_NOT_VALID         0x0c
#define ERR_TEMPLATE_UPLOAD            0x0d
#define ERR_CANNOT_RECEIVE_DATA_PACKAGES 0x0e
#define ERR_IMAGE_UPLOAD               0x0f
#define ERR_DELETE_TEMPLATE            0x10
#define ERR_CLEAR_LIBRARY              0x11
#define ERR_NO_VALID_PRIMARY_IMAGE     0x15
#define ERR_WRITE_FLASH                0x18
#define ERR_NO_DEFINITION              0x19
#define ERR_REGISTER_NO_INVALID        0x1a
#define ERR_INCORRECT_CONFIG_REG       0x1b
#define ERR_WRONG_NOTEPAD_PAGE_NO      0x1c
#define ERR_SERIAL_PORT                0x1d

int fpInit(uint8_t);
int fpClose(void);
void fpSetDebug(bool);
void fpSetDangerous(bool);
int fpCheckPacket(uint8_t *);
uint16_t calculateChecksum(uint8_t, uint16_t, uint8_t *);
void printPacket(uint8_t *);
int fpCreateCmdPacket(uint8_t, uint8_t *, uint8_t *);
int fpCreateDataPacket(uint8_t *, uint8_t *);
int fpCreateEndPacket(uint8_t *, uint8_t *);
int fpSendCmd(uint8_t, uint8_t *, uint8_t *);
int fpHandshake(void);
int fpReadSysPara(uint16_t *,uint16_t *, uint16_t *, uint16_t *,
		  uint32_t *, uint16_t *, uint16_t *);

int fpSetAddr(uint16_t);
int fpSetSysPara(uint8_t, uint8_t);
int fpReadConList(uint8_t,uint8_t *);
int fpTemplateNumber(uint16_t *);
int fpGenImg(void);
int fpUpImage(void);
int fpDownImage(uint8_t *);
int fpUpChar(uint8_t);
int fpDownChar(uint8_t);
int fpGetRandomNumber(uint32_t *);
int fpVerifyPassword(uint32_t);
int fpReadDataBuffer(uint8_t *,uint16_t *, uint8_t *);
int fpImg2Tz(uint8_t);
int fpStore(uint8_t,uint16_t);
int fpLoad(uint8_t,uint16_t);
int fpRegModel(void);
int fpCreateBitmap(uint8_t *, char *);
void fpPrintError(uint8_t);
uint8_t fpGetErrorCode(uint8_t *);
bool fpIsAcknowledgePacket(uint8_t *);
int fpSendCmd(uint8_t,uint8_t *, uint8_t *);
int fpSendCharBuf(uint8_t *);
int fpSendImage(uint8_t *);
int fpSendImageData(uint8_t *);
int fpSendData(uint8_t,uint8_t *);
int fpWriteNotepad(uint8_t, uint8_t *);
int fpReadNotepad(uint8_t, uint8_t *page);
int fpMatch(uint16_t *);
int fpSearch(uint8_t, uint16_t, uint16_t, uint16_t *, uint16_t *);
int fpEmpty(void);
#endif
