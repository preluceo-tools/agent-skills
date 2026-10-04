/* SPDX-License-Identifier: 0BSD */
/* GPIO, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * Blinks the LED every 500 ms; holding the button (pull-up, active low) freezes it.
 * Pins are an example (e.g. PF5 LED, PF6 button on a Curiosity Nano): check your board.
 * F_CPU must equal the OSC20M frequency set by the OSCCFG fuse (16 or 20 MHz). Fuses are not touched.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

#define LED_bm PIN5_bm
#define BTN_bm PIN6_bm

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0); /* reset default is prescaler /6; this turns it off */

    PORTF.DIRSET = LED_bm;
    PORTF.DIRCLR = BTN_bm;
    PORTF.PIN6CTRL = PORT_PULLUPEN_bm;

    for (;;) {
        if (PORTF.IN & BTN_bm) {      /* not pressed */
            PORTF.OUTTGL = LED_bm;    /* dedicated toggle register */
        }
        _delay_ms(500);
    }
}
