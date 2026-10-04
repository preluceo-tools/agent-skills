/* SPDX-License-Identifier: 0BSD */
/* TWI (I2C) master write, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * Writes one byte to a device at SLAVE_ADDR every 100 ms. TWINT is never cleared by hardware:
 * writing 1 to it starts the next step. The SCL divisor formula is the datasheet's, not part of the
 * validated research: check it against the datasheet. Without pull-ups every wait times out.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>
#include <util/twi.h>

#define SLAVE_ADDR 0x27 /* e.g. a PCF8574 backpack; use your device's 7-bit address */
#define SCL_HZ     100000UL

static uint8_t twi_wait(void)
{
    uint16_t n = 60000;
    while (!(TWCR & _BV(TWINT))) {
        if (--n == 0) {
            return 1;
        }
    }
    return 0;
}

static uint8_t twi_write(uint8_t addr7, uint8_t data)
{
    uint8_t err = 1;

    TWCR = _BV(TWINT) | _BV(TWSTA) | _BV(TWEN); /* START */
    if (twi_wait() || TW_STATUS != TW_START) {
        goto stop;
    }
    TWDR = (uint8_t)(addr7 << 1) | TW_WRITE;
    TWCR = _BV(TWINT) | _BV(TWEN);
    if (twi_wait() || TW_STATUS != TW_MT_SLA_ACK) {
        goto stop;
    }
    TWDR = data;
    TWCR = _BV(TWINT) | _BV(TWEN);
    if (twi_wait() || TW_STATUS != TW_MT_DATA_ACK) {
        goto stop;
    }
    err = 0;
stop:
    TWCR = _BV(TWINT) | _BV(TWEN) | _BV(TWSTO); /* STOP */
    return err;
}

int main(void)
{
    TWSR = 0;                                  /* prescaler 1 */
    TWBR = (uint8_t)((F_CPU / SCL_HZ - 16UL) / 2UL);
    for (;;) {
        (void)twi_write(SLAVE_ADDR, 0xFF);
        _delay_ms(100);
    }
}
