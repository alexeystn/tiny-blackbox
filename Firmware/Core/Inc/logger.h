#include "main.h"
#ifndef LOGGER_H
#define LOGGER_H

void Logger_Init(void);
enum status_t Logger_Loop(void);
void Logger_Stop(void);
void Logger_Dump(int numPages);
void Logger_SendStats(void);
void Logger_Erase(void);

uint8_t Logger_KeyPressed(void);
uint8_t Logger_KeyUnpressed(void);

#endif
