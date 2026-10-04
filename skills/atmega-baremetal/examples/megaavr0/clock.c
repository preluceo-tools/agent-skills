/* SPDX-License-Identifier: 0BSD */
/* Clock and F_CPU, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * After reset CLK_PER = CLK_MAIN / 6 (MCLKCTRLB = 0x11). MCLKCTRLB is CCP-protected: the key and
 * the write must be back to back, which _PROTECTED_WRITE() does. The main clock is OSC20M, running
 * at 16 or 20 MHz as the OSCCFG fuse says; read the fuse before choosing F_CPU. There is no crystal
 * oscillator above 32.768 kHz on this family.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

#define LED_bm PIN5_bm /* e.g. PF5: check your board */

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0); /* PEN = 0: CLK_PER = CLK_MAIN */

    PORTF.DIRSET = LED_bm;
    for (;;) {
        PORTF.OUTTGL = LED_bm;
        _delay_ms(250);
    }
}
