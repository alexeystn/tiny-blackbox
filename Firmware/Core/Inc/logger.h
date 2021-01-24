#include "main.h"
#ifndef LOGGER_H
#define LOGGER_H


void Logger_Init(void);
enum status_t Logger_WriteLoop(void);
enum status_t Logger_ReadLoop(void);
void Logger_Stop(void);
void Logger_Read(bool readFullMemory);
void Logger_SendInfo(void);
void Logger_Erase(void);
bool Logger_IsMemoryFull(void);

uint8_t Logger_KeyPressed(int delayMs);
uint8_t Logger_KeyUnpressed(int delayMs);

#endif
