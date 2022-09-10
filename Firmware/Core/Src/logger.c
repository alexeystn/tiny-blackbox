#include "logger.h"
#include "main.h"
#include "led.h"
#include "w25q.h"
#include "defines.h"


enum uartDmaFlag_t {
  DMA_FLAG_NONE,
  DMA_FLAG_HALF,
  DMA_FLAG_FULL,
};


volatile enum uartDmaFlag_t uartDmaFlag = DMA_FLAG_NONE;
uint8_t uartRxBuf[W25_PAGE_SIZE*2];
int pagePointer = 0;


void Logger_Erase(void)
{
  W25_WriteEnable();
  W25_ChipErase();
  while (W25_GetStatus()) {
    HAL_Delay(100);
  }
  pagePointer = 0;
}


void Logger_Read(bool readFullMemory)
{
  uint8_t buf[W25_PAGE_SIZE];
  int n;

  if (readFullMemory) {
    n = W25_PAGE_COUNT;
  } else {
    n = pagePointer;
  }

  for (int i = 0; i < n; i++) {
    W25_ReadPage(i, buf);
    HAL_UART_Transmit(HUART, buf, W25_PAGE_SIZE, HAL_MAX_DELAY);
  }
}


int Logger_FindFirstEmptyPage(void)
{
  uint8_t buf[W25_PAGE_SIZE];
  int left = 0;
  int right = W25_PAGE_COUNT;
  int mid;
  int result = right;
  bool pageErased;

  while (left < right) {
    mid = (left + right) / 2;
    W25_ReadPage(mid, buf);
    pageErased = true;
    for (int i = 0; i < W25_PAGE_SIZE; i++) {
      if (buf[i] != 0xFF) {
        pageErased = false;
        break;
      }
    }
    if (pageErased) {
      result = mid;
      right = mid;
    } else {
      left = mid + 1;
    }
  }
  return result;
}


static void Logger_SetUartBaudRate(int baudrate)
{
  (*HUART).Init.BaudRate = baudrate;
  HAL_UART_Init(HUART);
}


void Logger_Init(void)
{
  Logger_SetUartBaudRate(UART_BAUDRATE_WRITE);
  W25_ResetClock();
  pagePointer = Logger_FindFirstEmptyPage();
  HAL_UART_Receive_DMA(&huart1, uartRxBuf, W25_PAGE_SIZE*2);
}


void HAL_UART_RxHalfCpltCallback(UART_HandleTypeDef *huart)
{
  uartDmaFlag = DMA_FLAG_HALF;
}


void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  uartDmaFlag = DMA_FLAG_FULL;
}


enum status_t Logger_WriteLoop(void)
{
  static int prevRxTime = 0;
  static uint8_t *bufPointer;
  int currTime = HAL_GetTick();
  uint8_t flag = DMA_FLAG_NONE;

  flag = uartDmaFlag;

  if (flag != DMA_FLAG_NONE) {
    prevRxTime = currTime;
    uartDmaFlag = DMA_FLAG_NONE;

    if (flag == DMA_FLAG_HALF) {
      bufPointer = &uartRxBuf[0];
    }
    if (flag == DMA_FLAG_FULL) {
      bufPointer = &uartRxBuf[W25_PAGE_SIZE];
    }
    if (pagePointer < W25_PAGE_COUNT) {
      W25_WriteEnable();
      W25_WritePage(pagePointer, bufPointer, W25_PAGE_SIZE);
      while (W25_GetStatus()) {};
      pagePointer++;
    }
  }
  if ((currTime - prevRxTime) < 100) {
    return STATUS_BUSY;
  } else {
    return STATUS_IDLE_WRITE;
  }
}


void Logger_Stop(void)
{
  HAL_UART_AbortReceive(HUART);
  Logger_SetUartBaudRate(UART_BAUDRATE_READ);
}


bool Logger_IsMemoryFull(void)
{
  return (pagePointer >= W25_PAGE_COUNT);
}


void Logger_SendInfo(void)
{
  char str[100];
  int d = (1000 * pagePointer) / W25_PAGE_COUNT;
  sprintf(str, "Flash memory: %d.%d%% full\n", d/10, d%10 ); // @suppress("Float formatting support")
  HAL_UART_Transmit(HUART, (uint8_t*)str, strlen(str), HAL_MAX_DELAY);
}


uint8_t isKeyPressed(int delayMs)
{
  int endTime = HAL_GetTick() + delayMs;
  while (!HAL_GPIO_ReadPin(KEY_GPIO_Port, KEY_Pin)) {
    LED_DimLight();
    if (HAL_GetTick() > endTime)
      return 1;
  }
  return 0;
}


uint8_t isKeyUnpressed(int delayMs)
{
  int endTime = HAL_GetTick() + delayMs;
  while (HAL_GPIO_ReadPin(KEY_GPIO_Port, KEY_Pin)) {
    if (HAL_GetTick() > endTime)
      return 1;
  }
  return 0;
}
