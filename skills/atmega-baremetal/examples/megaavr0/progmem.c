/* SPDX-License-Identifier: 0BSD */
/* Flash tables, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * Flash is mapped into data space from 0x4000, so a plain const array stays in flash and plain loads
 * work. PROGMEM and pgm_read_*() still work and keep the code portable to Classic AVR.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/pgmspace.h>
#include <util/delay.h>

#define LED_bm PIN5_bm /* e.g. PF5: check your board */

static const uint16_t delays_ms[] = { 100, 200, 400, 800 };       /* plain const: stays in flash */
static const uint16_t delays_pm[] PROGMEM = { 100, 200, 400, 800 }; /* portable form */

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);
    PORTF.DIRSET = LED_bm;

    for (;;) {
        for (uint8_t i = 0; i < sizeof delays_ms / sizeof delays_ms[0]; i++) {
            uint16_t d = delays_ms[i];
            uint16_t e = pgm_read_word(&delays_pm[i]);
            PORTF.OUTTGL = LED_bm;
            while (d--) {
                _delay_ms(1);
            }
            while (e--) {
                _delay_ms(1);
            }
        }
    }
}
