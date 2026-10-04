/* SPDX-License-Identifier: 0BSD */
/* Timer1 8-bit fast PWM on OC1A, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * clk/64 at 16 MHz gives about 977 Hz. The duty ramps up and wraps.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

#if defined(__AVR_ATmega2560__)
#define OC1A_BIT PB5 /* OC1A is PB5 on the 2560 */
#else
#define OC1A_BIT PB1 /* OC1A is PB1 on the 328P */
#endif

int main(void)
{
    DDRB |= _BV(OC1A_BIT);
    TCCR1A = _BV(COM1A1) | _BV(WGM10);           /* fast PWM 8-bit (mode 5), clear OC1A on match */
    TCCR1B = _BV(WGM12) | _BV(CS11) | _BV(CS10); /* clk/64 */

    for (;;) {
        for (uint8_t duty = 0; duty < 255; duty++) {
            OCR1A = duty; /* 16-bit register: shares the TEMP byte, so never write it from main and an ISR */
            _delay_ms(4);
        }
    }
}
