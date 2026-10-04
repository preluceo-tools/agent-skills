/* SPDX-License-Identifier: 0BSD */
/* External (INT0) and pin-change (PCINT0) interrupts, Classic AVR.
 * Targets ATmega328P; also compiles for ATmega2560.
 * A falling edge on INT0 toggles the LED. Any change on PB0 (PCINT0) sets a flag for main().
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/interrupt.h>

#if defined(__AVR_ATmega2560__)
#define LED_BIT  PB7
#define INT0_BIT PD0 /* INT0 is PD0 on the 2560 */
#else
#define LED_BIT  PB5
#define INT0_BIT PD2 /* INT0 is PD2 on the 328P */
#endif

static volatile uint8_t pin_changed;

ISR(INT0_vect)
{
    PINB = _BV(LED_BIT); /* flag clears itself when the vector is taken */
}

ISR(PCINT0_vect)
{
    pin_changed = 1;
}

int main(void)
{
    DDRB |= _BV(LED_BIT);
    PORTD |= _BV(INT0_BIT);   /* pull-up */
    PORTB |= _BV(PB0);        /* pull-up on the pin-change input */

    EICRA = _BV(ISC01);       /* INT0 on falling edge */
    EIMSK = _BV(INT0);
    PCMSK0 = _BV(PCINT0);     /* PCINT0 = PB0 */
    PCICR = _BV(PCIE0);
    sei();

    for (;;) {
        if (pin_changed) {
            pin_changed = 0; /* single byte: the read-modify-write cannot be torn */
        }
    }
}
