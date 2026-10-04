/* SPDX-License-Identifier: 0BSD */
/* PROGMEM flash table, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * The delay table stays in flash. Classic AVR flash is a separate address space: a plain pointer
 * dereference reads SRAM, so every access goes through pgm_read_*.
 * Above 64 KB (ATmega2560) use pgm_read_*_far / PROGMEM_FAR for data placed past the first 64 KB.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/pgmspace.h>
#include <util/delay.h>

#if defined(__AVR_ATmega2560__)
#define LED_BIT PB7
#else
#define LED_BIT PB5
#endif

static const uint16_t delays_ms[] PROGMEM = { 100, 200, 400, 800 };

int main(void)
{
    DDRB |= _BV(LED_BIT);
    for (;;) {
        for (uint8_t i = 0; i < sizeof delays_ms / sizeof delays_ms[0]; i++) {
            uint16_t d = pgm_read_word(&delays_ms[i]);
            PINB = _BV(LED_BIT);
            while (d--) {
                _delay_ms(1); /* _delay_ms needs a constant argument */
            }
        }
    }
}
