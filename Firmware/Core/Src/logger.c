#include "main.h"
#include "w25q64.h"
#include <stdio.h>

#define KEY_PRESSED_TIME    2000
#define KEY_UNPRESSED_TIME  100

#define HUART    &huart1




uint8_t Logger_KeyPressed(void)
{
  int endTime = HAL_GetTick() + KEY_PRESSED_TIME;
  while (!HAL_GPIO_ReadPin(KEY_GPIO_Port, KEY_Pin)) {
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


uint8_t bufUartRx[W25_PAGE_SIZE*2];
int pagePointer = 0;

volatile uint8_t irq_flag = 0;

void HAL_UART_RxHalfCpltCallback(UART_HandleTypeDef *huart)
{
  irq_flag = 1;
  //HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
}


void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  irq_flag = 2;
  //HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
}



uint8_t Logger_IsPageEmpty(int n)
{
  uint8_t buf[W25_PAGE_SIZE];
  uint8_t res = 1;

  W25_ReadPage(n, buf);
  for (int j = 0; j < W25_PAGE_SIZE; j++) {
    if (buf[j] != 0xFF) {
      res = 0;
      break;
    }
  }
  return res;
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
  pagePointer = Logger_FindFirstEmptyPage();
  HAL_UART_Receive_DMA(&huart1, bufUartRx, W25_PAGE_SIZE*2);
}


int Logger_Loop(void)
{
  int result = 0;
  static int prevRxTime = 0;
  int currTime = HAL_GetTick();

  uint8_t r = 0;
  static uint8_t *pointer;

  r = irq_flag;

  if (r) {
    prevRxTime = currTime;

    irq_flag = 0;

    if (r == 1) { // half
      pointer = &bufUartRx[0];
    }
    if (r == 2) { // full
      pointer = &bufUartRx[W25_PAGE_SIZE];
    }

    W25_WriteEnable();
    W25_WritePage(pagePointer, pointer, W25_PAGE_SIZE);
    while (W25_GetStatus()) {};

    pagePointer++;

  }
  if ((currTime - prevRxTime) < 100)
    result = 1;
  else
    result = 0;
  if (pagePointer >= W25_PAGE_COUNT)
    result = -1;

  return result;
}



void Logger_Stop(void)
{
  HAL_UART_AbortReceive(HUART);
  HAL_UART_DMAStop(HUART);
}


void Logger_SendStats(void)
{
  char str[100];
  int d = (1000 * pagePointer)/W25_PAGE_COUNT;
  sprintf(str, "Flash memory: %d.%d%% full\n", d/10, d%10 );
  HAL_UART_Transmit(HUART, (uint8_t*)str, strlen(str), HAL_MAX_DELAY);
}



