#ifndef DAC6551_H
#define DAC6551_H

#include "stm32f4xx_hal.h"
#include <stdint.h>

typedef struct {
    SPI_HandleTypeDef *hspi;   // e.g., &hspi1
    GPIO_TypeDef      *cs_port; // e.g., GPIOB
    uint16_t           cs_pin;  // e.g., GPIO_PIN_6
    uint32_t           vref_mv; // e.g., 3300
} dac6551_t;

void dac6551_init(dac6551_t *d);
HAL_StatusTypeDef dac6551_write_code(dac6551_t *d, uint16_t code);
HAL_StatusTypeDef dac6551_set_mv(dac6551_t *d, uint32_t mv);

#endif // DAC6551_H
