#include "FreeRTOS.h"
#include "task.h"
#include "FreeRTOS_CLI.h"
//#include "usart.h"
#include "main.h"
#include "stm32f4xx_hal.h"
#include <string.h>

extern UART_HandleTypeDef huart2;

static char rx_line[64];
static char tx_buf[128];
static const char *prompt = "\r\n> ";

static BaseType_t prvUARTGetChar(char *ch, TickType_t to)
{
    if (HAL_UART_Receive(&huart2, (uint8_t*)ch, 1, to) == HAL_OK) return pdPASS;
    return pdFAIL;
}
static void UARTWrite(const char *s){ HAL_UART_Transmit(&huart2,(uint8_t*)s,strlen(s),HAL_MAX_DELAY); }

void vCliTask(void *arg)
{
    UARTWrite("\r\nDAC6551 CLI ready");
    UARTWrite(prompt);
    for (;;)
    {
        size_t len = 0; char c;
        while (len < sizeof(rx_line)-1) {
            if (prvUARTGetChar(&c, portMAX_DELAY) == pdPASS) {
                if (c=='\r' || c=='\n') { rx_line[len] = '\0'; break; }
                else if (c==0x7F || c=='\b') { if (len){ len--; UARTWrite("\b \b"); } }
                else { rx_line[len++]=c; HAL_UART_Transmit(&huart2,(uint8_t*)&c,1,HAL_MAX_DELAY); }
            }
        }

        BaseType_t more;
        do {
            more = FreeRTOS_CLIProcessCommand(rx_line, tx_buf, sizeof(tx_buf));
            UARTWrite("\r\n"); UARTWrite(tx_buf);
        } while (more != pdFALSE);

        UARTWrite(prompt);
    }
}
