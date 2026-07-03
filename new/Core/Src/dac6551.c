#include "dac6551.h"

static inline void cs_low(dac6551_t *d)  { HAL_GPIO_WritePin(d->cs_port, d->cs_pin, GPIO_PIN_RESET); }
static inline void cs_high(dac6551_t *d) { HAL_GPIO_WritePin(d->cs_port, d->cs_pin, GPIO_PIN_SET); }

void dac6551_init(dac6551_t *d)
{
    // CS idles HIGH (inactive) — the DAC's SYNC is active-low
    cs_high(d);

    // Optional: start at 0 V so the output is in a known state
    dac6551_write_code(d, 0);
}

HAL_StatusTypeDef dac6551_write_code(dac6551_t *d, uint16_t code)
{
    // 1) Clamp to 12-bit range (0..4095)
    if (code > 0x0FFF) code = 0x0FFF;

    // 2) Build the 24-bit frame as 3 bytes (MSB first):
    //    [23:18] = 000000 (don't care)
    //    [17:16] = PD1:PD0 = 00 (normal operation)
    //    [15:4]  = our 12-bit data, left-aligned
    //    [3:0]   = 0
    uint32_t frame = ((uint32_t)code) << 4;   // put 12 bits into [15:4]

    uint8_t tx[3];
    tx[0] = (frame >> 16) & 0xFF;  // bits [23:16]
    tx[1] = (frame >> 8)  & 0xFF;  // bits [15:8]
    tx[2] = (frame >> 0)  & 0xFF;  // bits [7:0]

    // 3) CS low for the whole 24-clock transfer, then high
    cs_low(d);
    HAL_StatusTypeDef s = HAL_SPI_Transmit(d->hspi, tx, 3, HAL_MAX_DELAY);
    cs_high(d);
    return s;
}

HAL_StatusTypeDef dac6551_set_mv(dac6551_t *d, uint32_t mv)
{
    // Clamp to full scale
    if (mv > d->vref_mv) mv = d->vref_mv;

    // Convert millivolts to a 12-bit code.
    // Full scale (4095) corresponds to vref_mv.
    // Multiply BEFORE dividing so we don't lose precision.
    uint32_t code = (mv * 4095UL) / d->vref_mv;

    return dac6551_write_code(d, (uint16_t)code);
}
