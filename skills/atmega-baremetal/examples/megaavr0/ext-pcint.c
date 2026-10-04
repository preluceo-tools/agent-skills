/* SPDX-License-Identifier: 0BSD */
/* Pin interrupts, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * There is no INTn / PCINTn split: each pin has its own sense setting (PINnCTRL.ISC) and each port
 * has one vector. The flag stays set until the ISR writes 1 to PORTx.INTFLAGS, so every ISR must.
 * A falling edge on the button pin toggles the LED.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/interrupt.h>

#define LED_bm PIN5_bm /* e.g. PF5: check your board */
#define BTN_bm PIN6_bm /* e.g. PF6 */

ISR(PORTF_PORT_vect)
{
    PORTF.INTFLAGS = BTN_bm; /* write 1 to clear; not cleared when the vector is taken */
    PORTF.OUTTGL = LED_bm;
}

int main(void)
{
    PORTF.DIRSET = LED_bm;
    PORTF.PIN6CTRL = PORT_PULLUPEN_bm | PORT_ISC_FALLING_gc;
    sei();
    for (;;) { }
}
