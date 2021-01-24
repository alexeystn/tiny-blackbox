#include "cli.h"
#include "defines.h"
#include "logger.h"

volatile enum cli_cmd_t latestCommand = 0;
bool commandNotRead = false;


#define CLI_RX_BUF_LEN  16
static int cliRxPnt = 0;
static uint8_t cliRxBuf[CLI_RX_BUF_LEN];
static uint8_t dummyByte;
bool cliEnabled = false;

const char cliCommands[CMD_N][CLI_RX_BUF_LEN] = {
    "info",
    "read",
    "dump",
    "erase"
};


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
      commandNotRead = true;
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
  if (cliRxPnt == CLI_RX_BUF_LEN) {
    cliRxPnt = 0;
  }
}


void CLI_Start(void)
{
  cliEnabled = true;
  HAL_UART_Receive_IT(HUART, &dummyByte, 1);
}


bool CLI_GetCommand(enum cli_cmd_t *cmd)
{
  if (commandNotRead) {
    *cmd = latestCommand;
    commandNotRead = false;
    return true;
  } else {
    return false;
  }
}
