/* SPDX-License-Identifier: 0BSD */
/* Clock and F_CPU, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * A fresh part ships on the internal 8 MHz RC with CKDIV8 programmed (1 MHz).
 * clock_prescale_set() does the timed CLKPR write. F_CPU must still equal the real clock:
 * here the source is 8 MHz, so build with F_CPU=8000000UL.
 * Build: make MCU=atmega328p F_CPU=8000000UL */
#include <avr/io.h>
#include <avr/power.h>
#include <util/delay.h>

#if defined(__AVR_ATmega2560__)
#define LED_BIT PB7
#else
#define LED_BIT PB5
#endif

int main(void)
{
    clock_prescale_set(clock_div_1); /* undo CKDIV8 at run time; the fuse itself stays as is */
    DDRB |= _BV(LED_BIT);
    for (;;) {
        PINB = _BV(LED_BIT);
        _delay_ms(250); /* argument must be a compile-time constant, optimisation on */
    }
}
