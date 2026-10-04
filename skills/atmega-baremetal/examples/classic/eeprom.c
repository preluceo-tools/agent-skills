/* SPDX-License-Identifier: 0BSD */
/* EEPROM, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * Counts boots in EEPROM and blinks that many times. eeprom_update_* skips the write when the byte
 * is unchanged, which saves wear. A blank cell reads 0xFF: the Makefile strips .eeprom (-R .eeprom),
 * so an EEMEM initialiser is not in firmware.hex. Treat 0xFF as "never written".
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/eeprom.h>
#include <util/delay.h>

#if defined(__AVR_ATmega2560__)
#define LED_BIT PB7
#else
#define LED_BIT PB5
#endif

static uint8_t boot_count EEMEM;

int main(void)
{
    uint8_t n = eeprom_read_byte(&boot_count);
    if (n == 0xFF) {
        n = 0;
    }
    n++;
    eeprom_update_byte(&boot_count, n);

    DDRB |= _BV(LED_BIT);
    for (;;) {
        for (uint8_t i = 0; i < n; i++) {
            PORTB |= _BV(LED_BIT);
            _delay_ms(150);
            PORTB &= ~_BV(LED_BIT);
            _delay_ms(150);
        }
        _delay_ms(1000);
    }
}
