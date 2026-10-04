/* SPDX-License-Identifier: 0BSD */
/* TWI0 host write, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * Writes one byte to a device at SLAVE_ADDR every 100 ms. Registers are TWI0.MCTRLA/MCTRLB/MSTATUS/
 * MBAUD/MADDR/MDATA. The MBAUD formula is the datasheet's, not part of the validated research, and
 * ignores bus rise time: check it. Without pull-ups every wait times out. Default pins are PA2/PA3.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

#define SLAVE_ADDR 0x27 /* e.g. a PCF8574 backpack; use your device's 7-bit address */
#define SCL_HZ     100000UL

static uint8_t twi_wait(void)
{
    uint16_t n = 60000;
    while (!(TWI0.MSTATUS & (TWI_WIF_bm | TWI_RIF_bm))) {
        if (--n == 0) {
            return 1;
        }
    }
    return 0;
}

static uint8_t twi_write(uint8_t addr7, uint8_t data)
{
    uint8_t err = 1;

    TWI0.MADDR = (uint8_t)(addr7 << 1); /* bit 0 = 0: write; sends START and the address */
    if (twi_wait() || (TWI0.MSTATUS & TWI_RXACK_bm)) {
        goto stop;
    }
    TWI0.MDATA = data;
    if (twi_wait() || (TWI0.MSTATUS & TWI_RXACK_bm)) {
        goto stop;
    }
    err = 0;
stop:
    TWI0.MCTRLB = TWI_MCMD_STOP_gc;
    return err;
}

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);

    TWI0.MBAUD = (uint8_t)((F_CPU / SCL_HZ - 10UL) / 2UL);
    TWI0.MCTRLA = TWI_ENABLE_bm;
    TWI0.MSTATUS = TWI_BUSSTATE_IDLE_gc; /* force the bus state to idle */

    for (;;) {
        (void)twi_write(SLAVE_ADDR, 0xFF);
        _delay_ms(100);
    }
}
