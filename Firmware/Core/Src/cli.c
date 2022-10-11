#include "cli.h"
#include "defines.h"
#include "logger.h"

#define CMD_MAX_LENGTH  16

volatile enum cli_cmd_t latestCommand = 0;
bool commandAvailable = false;
static int cliRxPnt = 0;
static uint8_t cliRxBuf[CMD_MAX_LENGTH];
bool cliEnabled = false;

const char cliCommands[CMD_N][CMD_MAX_LENGTH] = {
    "info",
    "read",
    "dump",
    "erase",
    "test"
};


void CLI_Start(void)
{
  static uint8_t dummyByte;
  cliEnabled = true;
  HAL_UART_Receive_IT(HUART, &dummyByte, 1);
}


static void CLI_ParseBuffer(int len)
{
  int icmd, ich;
  if (len <= 1)
    return;
  for (icmd = 0; icmd < CMD_N; icmd++) {
    bool res = true;
    for (ich = 0; ich < (len - 1); ich++) {
      if (cliCommands[icmd][ich] != cliRxBuf[ich]) {
        res = false;
        break;
      }
    }
    if (res == true) {
      latestCommand = icmd;
      commandAvailable = true;
      return;
    }
  }
}


void CLI_ProcessRxByte(uint8_t byte)
{
  cliRxBuf[cliRxPnt] = byte;
  cliRxPnt++;
  if (byte == '\n') {
    CLI_ParseBuffer(cliRxPnt);
    cliRxPnt = 0;
  }
  if (cliRxPnt == CMD_MAX_LENGTH) {
    cliRxPnt = 0;
  }
}


bool CLI_GetCommand(enum cli_cmd_t *cmd)
{
  if (commandAvailable) {
    *cmd = latestCommand;
    commandAvailable = false;
    return true;
  } else {
    return false;
  }
}
