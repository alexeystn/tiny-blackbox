#include "main.h"
#ifndef W25Q128_H
#define W25Q128_H


#define W25_PAGE_SIZE      256
#define W25_PAGE_COUNT     65536 // Q64 - 32768, Q128 - 65536


#define W25_WRITE_ENABLE  0x06 // bit must be set prior to every write/erase instruction
#define W25_JEDEC_ID      0x9F
#define W25_STATUS        0x05
#define W25_DATA_READ     0x03
#define W25_PAGE_PROGRAM  0x02
#define W25_CHIP_ERASE    0xC7


uint32_t W25_ReadID(void);


void W25_ResetClock(void);
void W25_Dump(void);
void W25_WriteEnable(void);
uint8_t W25_GetStatus(void);
void W25_ReadPage(int n, uint8_t *data);
void W25_WritePage(int page_num, uint8_t* data, uint16_t size);
void W25_ChipErase(void);


#endif
