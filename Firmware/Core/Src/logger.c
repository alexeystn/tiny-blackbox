#include "main.h"
#include "w25q64.h"


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






void LED_Blink(uint8_t n)
{
  for (int i = 0; i < n; i++) {
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
    HAL_Delay(100);
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
    HAL_Delay(100);
  }
}





void Logger_Erase(void)
{
  W25_WriteEnable();
  W25_ChipErase();
  while (W25_GetStatus()) {
    LED_Blink(1);
  }
}



void Logger_Dump(int n)
{
  uint8_t buf[W25_PAGE_SIZE];

  for (int i = 0; i < n; i++) {
    W25_ReadPage(n, buf);
    HAL_UART_Transmit(HUART, buf, W25_PAGE_SIZE, HAL_MAX_DELAY);
  }

}









uint8_t bufUartRx[W25_PAGE_SIZE*2];
int pagePointer = 0;

volatile uint8_t irq_flag = 0;

void HAL_UART_RxHalfCpltCallback(UART_HandleTypeDef *huart)
{
  irq_flag = 1;
  HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
}


void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  irq_flag = 2;
  HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
}


void Logger_Init(void)
{
  W25_ResetClock();
  // TODO: find first empty page
  HAL_UART_Receive_DMA(&huart1, bufUartRx, W25_PAGE_SIZE*2);
}


void Logger_Loop(void)
{
  uint8_t res = 0;
  static uint8_t *pointer;

  res = irq_flag;
  if (!res) {
    return;
  }
  irq_flag = 0;

  if (res == 1) { // half
    pointer = &bufUartRx[0];
  }
  if (res == 2) { // full
    pointer = &bufUartRx[W25_PAGE_SIZE];
  }

  W25_WriteEnable();
  W25_WritePage(pagePointer, pointer, W25_PAGE_SIZE);
  while (W25_GetStatus()) {};

  pagePointer++;
}



void Logger_Stop(void)
{

}






