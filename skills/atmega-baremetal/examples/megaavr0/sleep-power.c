/* SPDX-License-Identifier: 0BSD */
/* Sleep, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * <avr/sleep.h> drives SLPCTRL (modes: idle, standby, power-down). There is no PRR and no
 * power_*_disable() macros: stop a peripheral through its own enable bit.
 * Which wake sources work in power-down is not covered by the validated research: read the
 * datasheet before choosing power-down. This example idles and wakes on a TCA0 overflow.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>

#define LED_bm PIN5_bm /* e.g. PF5: check your board */

static volatile uint8_t tick;

ISR(TCA0_OVF_vect)
{
    TCA0.SINGLE.INTFLAGS = TCA_SINGLE_OVF_bm;
    tick = 1;
}

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);
    PORTF.DIRSET = LED_bm;

    TCA0.SINGLE.PER = (uint16_t)(F_CPU / 1024UL / 2UL - 1UL); /* 2 Hz at clk/1024 */
    TCA0.SINGLE.INTCTRL = TCA_SINGLE_OVF_bm;
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV1024_gc | TCA_SINGLE_ENABLE_bm;
    set_sleep_mode(SLEEP_MODE_IDLE);

    for (;;) {
        cli();
        if (!tick) {
            sleep_enable();
            sei();
            sleep_cpu();
            sleep_disable();
        }
        sei();
        if (tick) {
            tick = 0;
            PORTF.OUTTGL = LED_bm;
        }
    }
}
