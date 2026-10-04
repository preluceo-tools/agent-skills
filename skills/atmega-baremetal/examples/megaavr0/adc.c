/* SPDX-License-Identifier: 0BSD */
/* ADC0 single conversions, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * Reads AIN0 (PD0 on the 4809) against VDD; the LED is on while the reading is above mid-scale.
 * ADC clock must be 50 kHz to 1.5 MHz for full resolution: 16 MHz / 16 = 1 MHz.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>

#define LED_bm PIN5_bm /* e.g. PF5: check your board */

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);

    PORTF.DIRSET = LED_bm;
    PORTD.PIN0CTRL = PORT_ISC_INPUT_DISABLE_gc; /* analog pin: digital input buffer off */
    ADC0.CTRLC = ADC_PRESC_DIV16_gc | ADC_REFSEL_VDDREF_gc;
    ADC0.MUXPOS = ADC_MUXPOS_AIN0_gc;
    ADC0.CTRLA = ADC_ENABLE_bm;

    for (;;) {
        ADC0.COMMAND = ADC_STCONV_bm;
        while (!(ADC0.INTFLAGS & ADC_RESRDY_bm)) { }
        if (ADC0.RES > 512) { /* reading RES clears RESRDY */
            PORTF.OUTSET = LED_bm;
        } else {
            PORTF.OUTCLR = LED_bm;
        }
    }
}
