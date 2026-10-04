/* SPDX-License-Identifier: 0BSD */
/* GPIO, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * Blinks the LED every 500 ms; holding the button (pull-up, active low) freezes it.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

#if defined(__AVR_ATmega2560__)
#define LED_BIT PB7 /* Arduino Mega pin 13 */
#else
#define LED_BIT PB5 /* Uno/Nano pin 13 */
#endif
#define BTN_BIT PB0

int main(void)
{
    DDRB |= _BV(LED_BIT);   /* DDR 1 = output */
    DDRB &= ~_BV(BTN_BIT);  /* DDR 0 = input */
    PORTB |= _BV(BTN_BIT);  /* input + PORT 1 = pull-up on */

    for (;;) {
        if (PINB & _BV(BTN_BIT)) { /* not pressed */
            PINB = _BV(LED_BIT);   /* writing 1 to PINx toggles PORTx (absent on ATmega8/8A) */
        }
        _delay_ms(500);
    }
}
