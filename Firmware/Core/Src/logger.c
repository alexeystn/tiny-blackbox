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


static void Send_SelfTest_Result(bool result, int avg, int max)
{
  static char buf[64];
  char res[16];
  if (result) {
    sprintf(res, "OK");
  } else {
    sprintf(res, "FAIL");
  }
  sprintf(buf, "Self-test result: %s\n", res);
  HAL_UART_Transmit(HUART, (uint8_t*)buf, strlen(buf), HAL_MAX_DELAY);
  sprintf(buf, "Average page write time: %d us\n", avg);
  HAL_UART_Transmit(HUART, (uint8_t*)buf, strlen(buf), HAL_MAX_DELAY);
  sprintf(buf, "Max page write time: %d us\n", max);
  HAL_UART_Transmit(HUART, (uint8_t*)buf, strlen(buf), HAL_MAX_DELAY);
}


static void Send_Done(void)
{
  static const char buf[] = "Done\n";
  HAL_UART_Transmit(HUART, (uint8_t*)buf, strlen(buf), HAL_MAX_DELAY);
}


#define HEARTBEAT_PERIOD_MS 250
static void Send_Heartbeat(void)
{
  static const char buf[] = ".\n";
  static int previousTimeMs = 0;
  int currentTimeMs = HAL_GetTick();
  if ((currentTimeMs - previousTimeMs) > HEARTBEAT_PERIOD_MS) {
    previousTimeMs = currentTimeMs + HEARTBEAT_PERIOD_MS;
    HAL_UART_Transmit(HUART, (uint8_t*)buf, strlen(buf), HAL_MAX_DELAY);
  }
}


void Logger_SelfTest(void)
{
  uint8_t buf[W25_PAGE_SIZE + 1];
  uint8_t bufCompare[W25_PAGE_SIZE];
  int counter = 0;
  bool result = true;
  uint32_t time, sum = 0, max = 0;

  // Fill memory with incrementing numbers:
  // 00000000 00000001 00000002 ...
  for (int page = 0; page < W25_PAGE_COUNT; page++) {
    for (int number = 0; number < (W25_PAGE_SIZE/8); number++) {
      sprintf((char*)buf + number*8, "%08d", counter);
      counter++;
    }
    W25_WriteEnable();
    W25_WritePage(page, buf, W25_PAGE_SIZE);
    RESET_TIMER_US;
    while (W25_GetStatus()) {};
    time = GET_TIMER_US;
    if (time > max) {
      max = time;
    }
    sum += time;
    Send_Heartbeat();
  }
  pagePointer = W25_PAGE_COUNT;
  counter = 0;
  for (int page = 0; page < W25_PAGE_COUNT; page++) {
    for (int number = 0; number < (W25_PAGE_SIZE/8); number++) {
      sprintf((char*)buf + number*8, "%08d", counter);
      counter++;
    }
    W25_ReadPage(page, bufCompare);
    if (memcmp(bufCompare, buf, W25_PAGE_SIZE) != 0) {
      result = false;
    }
    Send_Heartbeat();
  }
  Send_SelfTest_Result(result, sum / W25_PAGE_COUNT, max);
  Send_Done();
}


void Logger_Erase(void)
{
  W25_WriteEnable();
  W25_ChipErase();
  while (W25_GetStatus()) {
    HAL_Delay(HEARTBEAT_PERIOD_MS);
    Send_Heartbeat();
  }
  Send_Done();
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
  HAL_TIM_Base_Start(HTIM_US);
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
