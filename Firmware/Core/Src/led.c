#include "main.h"
#include "led.h"
#include "defines.h"

const uint8_t sequenceSingleBlink[] = {150, 2, 0};
const uint8_t sequenceDoubleBlink[] = {100, 2, 20, 2, 0};
const uint8_t sequenceFastBlink[] = {10, 10, 0};
const uint8_t sequenceFull[] = {20, 2, 20, 2, 20, 2, 20, 100, 0};
const uint8_t sequenceError[] = {10, 2, 10, 2, 10, 2, 10, 2, 30, 2, 30, 2, 30, 2, 20, 0};

const uint8_t *activeSequence = sequenceSingleBlink;
uint8_t seqPnt = 0;
static int nextToggleTime = 0;
bool ledStatusEnabled = true;


void LED_Init(void)
{
  HAL_TIM_Base_Start_IT(HTIM_LED);
}


void LED_SetStatus(enum status_t st)
{
  static enum status_t prevLedStatus = STATUS_IDLE_WRITE;

  if (st != prevLedStatus) {
    ledStatusEnabled = false;
    switch (st) {
    case STATUS_IDLE_WRITE:
      activeSequence = sequenceSingleBlink;
      break;
    case STATUS_IDLE_READ:
      activeSequence = sequenceDoubleBlink;
      break;
    case STATUS_BUSY:
      activeSequence = sequenceFastBlink;
      break;
    case STATUS_FULL:
      activeSequence = sequenceFull;
      break;
    case STATUS_ERROR:
      activeSequence = sequenceError;
      break;
    }
    seqPnt = 0;
    nextToggleTime = 0;
    prevLedStatus = st;
    ledStatusEnabled = true;
  }
}


void LED_Handle(void)
{
  int currentTime = HAL_GetTick();
  if (currentTime >= nextToggleTime) {
    nextToggleTime = currentTime + activeSequence[seqPnt]*10;
    if (seqPnt & 0x01) {
      LED_ON;
    } else {
      LED_OFF;
    }
    seqPnt++;
    if (activeSequence[seqPnt] == 0) {
      seqPnt = 0;
    }
  }
}


void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  if ((htim == HTIM_LED) && (ledStatusEnabled)) {
    LED_Handle();
  }
}


void LED_Blink(uint8_t n)
{
  ledStatusEnabled = false;
  for (int i = 0; i < n; i++) {
    LED_ON;
    HAL_Delay(150);
    LED_OFF;
    HAL_Delay(150);
  }
  HAL_Delay(100);
  ledStatusEnabled = true;
}


void LED_DimLight(void)
{
  // 5% duty cycle to emulate dim light
  ledStatusEnabled = false;
  LED_ON;
  HAL_Delay(1);
  LED_OFF;
  HAL_Delay(20);
  ledStatusEnabled = true;
}
