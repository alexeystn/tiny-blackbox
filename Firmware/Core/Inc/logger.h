#ifndef LOGGER_H
#define LOGGER_H

#include "main.h"

void Logger_Init(void);
enum status_t Logger_WriteLoop(void);
void Logger_Stop(void);
void Logger_Read(bool readFullMemory);
void Logger_SendInfo(void);
void Logger_Erase(void);
bool Logger_IsMemoryFull(void);

uint8_t isKeyPressed(int delayMs);
uint8_t isKeyUnpressed(int delayMs);

#endif
