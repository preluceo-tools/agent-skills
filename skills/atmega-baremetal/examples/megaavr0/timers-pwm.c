/* SPDX-License-Identifier: 0BSD */
/* TCA0 single-slope PWM on WO0, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * TCA0 is a 16-bit timer with no ICP pin. WO0 is PA0 on the default port mux (check the datasheet
 * for your package). The duty is written to CMP0BUF so it takes effect at the next period.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);

    PORTA.DIRSET = PIN0_bm;
    TCA0.SINGLE.PER = 255;
    TCA0.SINGLE.CTRLB = TCA_SINGLE_CMP0EN_bm | TCA_SINGLE_WGMODE_SINGLESLOPE_gc;
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV64_gc | TCA_SINGLE_ENABLE_bm;

    for (;;) {
        for (uint8_t duty = 0; duty < 255; duty++) {
            TCA0.SINGLE.CMP0BUF = duty;
            _delay_ms(4);
        }
    }
}
