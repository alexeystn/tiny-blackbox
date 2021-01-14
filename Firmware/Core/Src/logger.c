#include <w25q.h>
#include "main.h"
#include "led.h"

#define KEY_PRESSED_TIME    2000
#define KEY_UNPRESSED_TIME  100

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
  const char str1[] = "Erasing memory...\n";
  const char str2[] = "Done. Reboot...\n";
  HAL_UART_Transmit(HUART, (uint8_t*)str1, strlen(str1), HAL_MAX_DELAY);
  W25_WriteEnable();
  W25_ChipErase();
  while (W25_GetStatus()) {
    HAL_Delay(100);
  }
  HAL_UART_Transmit(HUART, (uint8_t*)str2, strlen(str2), HAL_MAX_DELAY);
}


void Logger_Dump(int n)
{
  uint8_t buf[W25_PAGE_SIZE];

  for (int i = 0; i < n; i++) {
    W25_ReadPage(i, buf);
    HAL_UART_Transmit(HUART, buf, W25_PAGE_SIZE, HAL_MAX_DELAY);
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


void Logger_Init(void)
{
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


enum status_t Logger_Loop(void)
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
}


bool Logger_IsMemoryFull(void)
{
  return (pageCounter >= W25_PAGE_COUNT);
}


void Logger_SendStats(void)
{
  char str[100];
  int d = (1000 * pageCounter)/W25_PAGE_COUNT;
  sprintf(str, "Flash memory: %d.%d%% full\n", d/10, d%10 ); // @suppress("Float formatting support")
  HAL_UART_Transmit(HUART, (uint8_t*)str, strlen(str), HAL_MAX_DELAY);
}


uint8_t Logger_KeyPressed(void)
{
  int endTime = HAL_GetTick() + KEY_PRESSED_TIME;
  while (!HAL_GPIO_ReadPin(KEY_GPIO_Port, KEY_Pin)) {
    LED_BlinkShort();
    if (HAL_GetTick() > endTime)
      return 1;
  }
  return 0;
}


uint8_t Logger_KeyUnpressed(void)
{
  int endTime = HAL_GetTick() + KEY_UNPRESSED_TIME;
  while (HAL_GPIO_ReadPin(KEY_GPIO_Port, KEY_Pin)) {
    if (HAL_GetTick() > endTime)
      return 1;
  }
  return 0;
}
