/* SPDX-License-Identifier: 0BSD */
/* ISR and atomic rules, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * TCA0 overflow makes a 1 ms tick; main() reads the 32-bit counter inside ATOMIC_BLOCK.
 * Write 1 to TCA0.SINGLE.INTFLAGS in the ISR: the flag is not cleared by taking the vector.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>

#define LED_bm PIN5_bm /* e.g. PF5: check your board */

static volatile uint32_t ms;

ISR(TCA0_OVF_vect)
{
    TCA0.SINGLE.INTFLAGS = TCA_SINGLE_OVF_bm;
    ms++;
}

static uint32_t ms_now(void)
{
    uint32_t t;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        t = ms;
    }
    return t;
}

int main(void)
{
    uint32_t last = 0;

    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);
    PORTF.DIRSET = LED_bm;

    TCA0.SINGLE.PER = (uint16_t)(F_CPU / 64UL / 1000UL - 1UL); /* 1 kHz at clk/64 */
    TCA0.SINGLE.INTCTRL = TCA_SINGLE_OVF_bm;
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV64_gc | TCA_SINGLE_ENABLE_bm;
    sei();

    for (;;) {
        uint32_t now = ms_now();
        if (now - last >= 500) {
            last = now;
            PORTF.OUTTGL = LED_bm;
        }
    }
}
