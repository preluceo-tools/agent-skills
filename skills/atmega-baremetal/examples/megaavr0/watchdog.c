/* SPDX-License-Identifier: 0BSD */
/* Watchdog, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * WDT.CTRLA is CCP-protected; <avr/wdt.h> handles that. There is no MCUSR/WDRF: the reset cause is
 * in RSTCTRL.RSTFR (write 1 to clear). Remove wdt_reset() to watch the chip reset.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/wdt.h>
#include <util/delay.h>

#define LED_bm PIN5_bm /* e.g. PF5: check your board */

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);

    uint8_t cause = RSTCTRL.RSTFR; /* read the reset cause, then clear it */
    RSTCTRL.RSTFR = cause;
    (void)cause;

    PORTF.DIRSET = LED_bm;
    wdt_enable(WDTO_1S);
    for (;;) {
        PORTF.OUTTGL = LED_bm;
        _delay_ms(200);
        wdt_reset();
    }
}
