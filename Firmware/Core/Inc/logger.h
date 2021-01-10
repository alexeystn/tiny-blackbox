#include "main.h"
#ifndef LOGGER_H
#define LOGGER_H

void Logger_Init(void);
void Logger_Loop(void);
void Logger_Stop(void);

uint8_t Logger_KeyPressed(void);
uint8_t Logger_KeyUnpressed(void);

void Logger_Erase(void);
void LED_Blink(uint8_t n);

void Logger_Dump(int numPages);


#endif
