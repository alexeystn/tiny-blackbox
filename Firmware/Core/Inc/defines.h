#ifndef DEFINES_H
#define DEFINES_H

#define HUART        &huart1
#define HSPI         &hspi1
#define HTIM_LED     &htim17

#define UART_BAUDRATE_WRITE  1500000
#define UART_BAUDRATE_READ    500000

#define TEST_PIN_ON()  HAL_GPIO_WritePin(TEST_POINT_GPIO_Port, TEST_POINT_Pin, GPIO_PIN_SET)
#define TEST_PIN_OFF()  HAL_GPIO_WritePin(TEST_POINT_GPIO_Port, TEST_POINT_Pin, GPIO_PIN_RESET)

#endif
