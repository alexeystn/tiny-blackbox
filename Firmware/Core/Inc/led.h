#ifndef LED_H
#define LED_H

#include "main.h"

enum status_t {
  STATUS_IDLE_WRITE,
  STATUS_IDLE_READ,
  STATUS_BUSY,
  STATUS_FULL
};

#define LED_OFF   LED_GPIO_Port->BRR = LED_Pin
#define LED_ON    LED_GPIO_Port->BSRR = LED_Pin

void LED_Init(void);
void LED_SetStatus(enum status_t status);
void LED_Blink(uint8_t n);
void LED_DimLight(void);

#endif
