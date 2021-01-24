#include "main.h"
#ifndef CLI_H
#define CLI_H

enum cli_cmd_t {
  CMD_INFO,
  CMD_READ,
  CMD_DUMP,
  CMD_ERASE,
  CMD_N
};

extern bool cliEnabled;

void CLI_Start();
void CLI_ProcessRxByte(uint8_t byte);
bool CLI_GetCommand(enum cli_cmd_t *cmd);

#endif
