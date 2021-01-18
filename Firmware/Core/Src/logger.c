#include "logger.h"
#include "main.h"
#include "led.h"
#include "w25q.h"

#define HUART    &huart1


enum dmaFlagUART_t {
  DMA_FLAG_NONE,
  DMA_FLAG_HALF,
  DMA_FLAG_FULL,
};


volatile enum dmaFlagUART_t dmaFlagUart = DMA_FLAG_NONE;
uint8_t bufUartRx[W25_PAGE_SIZE*2];
int pageCounter = 0;


void Logger_Erase(void)
{
  W25_WriteEnable();
  W25_ChipErase();
  while (W25_GetStatus()) {
    HAL_Delay(100);
  }
}


void Logger_Dump(int n)
{
  uint8_t buf[W25_PAGE_SIZE];

  for (int i = 0; i < n; i++) {
    W25_ReadPage(i, buf);
    HAL_UART_Transmit(HUART, buf, W25_PAGE_SIZE, HAL_MAX_DELAY);
  }
}


enum status_t Logger_ReadLoop(void)
{
  static int readPageCounter = 0;
  uint8_t buf[W25_PAGE_SIZE];

  if (readPageCounter < W25_PAGE_COUNT) {

    W25_ReadPage(readPageCounter, buf);
    HAL_UART_Transmit(HUART, buf, W25_PAGE_SIZE, HAL_MAX_DELAY);
    readPageCounter++;
    return ST_BUSY;
  } else {
    return ST_IDLE_READ;
  }
}


bool Logger_IsPageEmpty(int n)
{
  uint8_t buf[W25_PAGE_SIZE];

  W25_ReadPage(n, buf);
  for (int j = 0; j < W25_PAGE_SIZE; j++) {
    if (buf[j] != 0xFF) {
      return false;
      break;
    }
  }
  return true;
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
  pageCounter = Logger_FindFirstEmptyPage();
  HAL_UART_Receive_DMA(&huart1, bufUartRx, W25_PAGE_SIZE*2);
}


void HAL_UART_RxHalfCpltCallback(UART_HandleTypeDef *huart)
{
  dmaFlagUart = DMA_FLAG_HALF;
}


void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  dmaFlagUart = DMA_FLAG_FULL;
}


enum status_t Logger_WriteLoop(void)
{
  static int prevRxTime = 0;
  static uint8_t *bufPointer;
  int currTime = HAL_GetTick();
  uint8_t flag = DMA_FLAG_NONE;

  flag = dmaFlagUart;

  if (flag != DMA_FLAG_NONE) {
    prevRxTime = currTime;
    dmaFlagUart = DMA_FLAG_NONE;

    if (flag == DMA_FLAG_HALF) {
      bufPointer = &bufUartRx[0];
    }
    if (flag == DMA_FLAG_FULL) {
      bufPointer = &bufUartRx[W25_PAGE_SIZE];
    }
    if (pageCounter < W25_PAGE_COUNT) {
      W25_WriteEnable();
      W25_WritePage(pageCounter, bufPointer, W25_PAGE_SIZE);
      while (W25_GetStatus()) {};
    }
    pageCounter++;
  }
  if ((currTime - prevRxTime) < 100) {
    return ST_BUSY;
  } else {
    return ST_IDLE_WRITE;
  }
}


void Logger_Stop(void)
{
  HAL_UART_AbortReceive(HUART);
  Logger_SetUartBaudRate(UART_BAUDRATE_READ);
}


bool Logger_IsMemoryFull(void)
{
  return (pageCounter >= W25_PAGE_COUNT);
}


void Logger_SendStats(void)
{
  int d[2];
  d[0] = 0xAABBCCDD;
  d[1] = (1000 * pageCounter)/W25_PAGE_COUNT;
  HAL_UART_Transmit(HUART, (uint8_t*)d, sizeof(d), HAL_MAX_DELAY);
}


uint8_t Logger_KeyPressed(int delayMs)
{
  int endTime = HAL_GetTick() + delayMs;
  while (!HAL_GPIO_ReadPin(KEY_GPIO_Port, KEY_Pin)) {
    LED_BlinkShort();
    if (HAL_GetTick() > endTime)
      return 1;
  }
  return 0;
}


uint8_t Logger_KeyUnpressed(int delayMs)
{
  int endTime = HAL_GetTick() + delayMs;
  while (HAL_GPIO_ReadPin(KEY_GPIO_Port, KEY_Pin)) {
    if (HAL_GetTick() > endTime)
      return 1;
  }
  return 0;
}
