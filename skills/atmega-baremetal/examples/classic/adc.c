/* SPDX-License-Identifier: 0BSD */
/* ADC single conversions, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * Reads channel ADC0 against AVcc; the LED is on while the reading is above mid-scale.
 * Prescaler /128 gives a 125 kHz ADC clock at 16 MHz.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>

#if defined(__AVR_ATmega2560__)
#define LED_BIT PB7
#else
#define LED_BIT PB5
#endif

int main(void)
{
    DDRB |= _BV(LED_BIT);
    ADMUX = _BV(REFS0);                                        /* AVcc reference, channel 0 */
    ADCSRA = _BV(ADEN) | _BV(ADPS2) | _BV(ADPS1) | _BV(ADPS0); /* enable, clk/128 */

    for (;;) {
        ADCSRA |= _BV(ADSC);
        while (ADCSRA & _BV(ADSC)) { } /* ADSC clears when the conversion is done */
        if (ADC > 512) {
            PORTB |= _BV(LED_BIT);
        } else {
            PORTB &= ~_BV(LED_BIT);
        }
    }
}
