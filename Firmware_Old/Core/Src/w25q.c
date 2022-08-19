#include "w25q.h"
#include "main.h"
#include "defines.h"

#define SPI_ON   SPI1_NSS_GPIO_Port->BRR = SPI1_NSS_Pin
#define SPI_OFF  SPI1_NSS_GPIO_Port->BSRR = SPI1_NSS_Pin

static uint8_t spiTxBuf[4];
static uint8_t spiRxBuf[4];

volatile uint8_t spiDmaFlag = 0;


void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi)
{
  spiDmaFlag = 1;
}


void HAL_SPI_RxCpltCallback(SPI_HandleTypeDef *hspi)
{
  spiDmaFlag = 1;
}


static void DMA_Wait()
{
  while (!spiDmaFlag) {};
  spiDmaFlag = 0;
}


static void W25_Delay(void)
{
  for (volatile int i = 0; i < 100; i++) {
    asm("nop");
  }
}


void W25_ResetClock(void)
{
  // Turns clock line from undefined state to low
  spiTxBuf[0] = 0;
  HAL_SPI_Transmit(HSPI, spiTxBuf, 1, HAL_MAX_DELAY);
  W25_Delay();
}


uint32_t W25_ReadID(void)
{
  uint32_t res;
  spiTxBuf[0] = W25_JEDEC_ID;
  SPI_ON;
  HAL_SPI_TransmitReceive(HSPI, spiTxBuf, spiRxBuf, 4, HAL_MAX_DELAY);
  SPI_OFF;
  res = (spiRxBuf[1] << 16) | (spiRxBuf[2] << 8) | (spiRxBuf[3] << 0);
  return res;
}



void W25_ReadPage(int n, uint8_t *buf)
{
  uint32_t address;
  address = n * W25_PAGE_SIZE;
  spiTxBuf[0] = W25_DATA_READ;
  spiTxBuf[1] = (address >> 16) & 0xFF;
  spiTxBuf[2] = (address >> 8) & 0xFF;
  spiTxBuf[3] = (address >> 0) & 0xFF;
  SPI_ON;
  HAL_SPI_Transmit(HSPI, spiTxBuf, 4, HAL_MAX_DELAY);
  HAL_SPI_Receive_DMA(HSPI, buf, W25_PAGE_SIZE);
  DMA_Wait();
  SPI_OFF;
}


void W25_WriteEnable(void)
{
  spiTxBuf[0] = W25_WRITE_ENABLE;
  SPI_ON;
  HAL_SPI_Transmit(HSPI, spiTxBuf, 1, HAL_MAX_DELAY);
  SPI_OFF;
  W25_Delay();
}


uint8_t W25_GetStatus(void)
{
  spiTxBuf[0] = W25_STATUS;
  SPI_ON;
  HAL_SPI_TransmitReceive(HSPI, spiTxBuf, spiRxBuf, 2, HAL_MAX_DELAY);
  SPI_OFF;
  W25_Delay();
  return (spiRxBuf[1] & 0x01);
}


void W25_WritePage(int pageNum, uint8_t* data, uint16_t size)
{
  uint32_t address = pageNum * W25_PAGE_SIZE;
  spiTxBuf[0] = W25_PAGE_PROGRAM;
  spiTxBuf[1] = (address >> 16) & 0xFF;
  spiTxBuf[2] = (address >> 8) & 0xFF;
  spiTxBuf[3] = 0;
  SPI_ON;
  HAL_SPI_Transmit(HSPI, spiTxBuf, 4, HAL_MAX_DELAY);
  HAL_SPI_Transmit_DMA(HSPI, data, size);
  DMA_Wait();
  SPI_OFF;
  W25_Delay();
}


void W25_ChipErase(void)
{
  spiTxBuf[0] = W25_CHIP_ERASE;
  SPI_ON;
  HAL_SPI_Transmit(HSPI, spiTxBuf, 1, HAL_MAX_DELAY);
  SPI_OFF;
  W25_Delay();
}
