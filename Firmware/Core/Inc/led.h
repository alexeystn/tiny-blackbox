#include "main.h"
#ifndef LED_H
#define LED_H

enum status_t {
  ST_IDLE_WRITE,
  ST_IDLE_READ,
  ST_BUSY,
  ST_FULL
};

#define LED_OFF   LED_GPIO_Port->BRR = LED_Pin
#define LED_ON    LED_GPIO_Port->BSRR = LED_Pin

void LED_Init(void);
void LED_SetStatus(enum status_t status);
void LED_Handle(void);
void LED_Blink(uint8_t n);
void LED_BlinkShort(void);

#endif