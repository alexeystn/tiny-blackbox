#ifndef CLI_H
#define CLI_H

#include "main.h"

enum cli_cmd_t {
  CMD_INFO,
  CMD_READ,
  CMD_DUMP,
  CMD_ERASE,
  CMD_TEST,
  CMD_N
};

extern bool cliEnabled;

void CLI_Start();
void CLI_ProcessRxByte(uint8_t byte);
bool CLI_GetCommand(enum cli_cmd_t *cmd);

#endif
