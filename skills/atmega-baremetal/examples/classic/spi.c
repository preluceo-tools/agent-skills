/* SPDX-License-Identifier: 0BSD */
/* SPI master, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * Sends one byte every 10 ms with a manual chip select. Pin map is from the datasheet pinout:
 * check it against the target chip.
 * Keep the SS pin an output (or held high): a low level on an input SS drops the master to slave.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

#if defined(__AVR_ATmega2560__)
#define SS_BIT   PB0
#define SCK_BIT  PB1
#define MOSI_BIT PB2
#else
#define SS_BIT   PB2
#define MOSI_BIT PB3
#define SCK_BIT  PB5
#endif

static uint8_t spi_xfer(uint8_t b)
{
    SPDR = b;
    while (!(SPSR & _BV(SPIF))) { }
    return SPDR;
}

int main(void)
{
    PORTB |= _BV(SS_BIT); /* chip select idles high */
    DDRB |= _BV(SS_BIT) | _BV(MOSI_BIT) | _BV(SCK_BIT);
    SPCR = _BV(SPE) | _BV(MSTR) | _BV(SPR0); /* master, mode 0, fosc/16 */

    for (;;) {
        PORTB &= ~_BV(SS_BIT);
        (void)spi_xfer(0xA5);
        PORTB |= _BV(SS_BIT);
        _delay_ms(10);
    }
}
