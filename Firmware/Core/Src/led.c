#include "main.h"
#include "led.h"

const uint8_t sequenceSingleBlink[] = {150, 2, 0};
const uint8_t sequenceDoubleBlink[] = {150, 2, 20, 2, 0};
const uint8_t sequenceFastBlink[] = {10, 10, 0};
const uint8_t sequenceFull[] = {2, 30, 2, 30, 20, 20, 20, 20, 0};


bool ledStatusEnabled = true;

const uint8_t *seq = sequenceSingleBlink;
uint8_t pnt = 0;
int nextTime = 0;

void LED_Init(void)
{
  HAL_TIM_Base_Start_IT(&htim17);
}


void LED_SetStatus(enum status_t status)
{
  static enum status_t prevStatus = IDLE_1;

  if (status != prevStatus) {
    switch (status) {
    case IDLE_1:
      seq = sequenceSingleBlink;
      break;
    case IDLE_2:
      seq = sequenceDoubleBlink;
      break;
    case BUSY:
      seq = sequenceFastBlink;
      break;
    case FULL:
      seq = sequenceFull;
      break;
    }
    pnt = 0;
    nextTime = 0;
    prevStatus = status;
  }
}


void LED_Handle(void)
{

  int currentTime = HAL_GetTick();
  if (currentTime > nextTime) {
    if (pnt & 0x01) {
      LED_OFF;
    } else {
      LED_ON;
    }
    pnt++;
    if (seq[pnt] == 0) {
      pnt = 0;
    }
    nextTime = currentTime + seq[pnt]*10;
  }
}


void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  // TODO: check if TIM17
  if (ledStatusEnabled) {
    LED_Handle();
  }
}


void LED_Blink(uint8_t n)
{
  ledStatusEnabled = false;
  for (int i = 0; i < n; i++) {
    LED_ON;
    HAL_Delay(100);
    LED_OFF;
    HAL_Delay(100);
  }
  ledStatusEnabled = true;
}
