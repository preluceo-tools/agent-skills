/* SPDX-License-Identifier: 0BSD */
/* EEPROM, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * Counts boots in EEPROM and blinks that many times. EEPROM is memory-mapped at 0x1400 and written
 * through NVMCTRL commands; <avr/eeprom.h> hides that. A blank cell reads 0xFF and the Makefile
 * strips .eeprom (-R .eeprom), so an EEMEM initialiser is not in firmware.hex.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/eeprom.h>
#include <util/delay.h>

#define LED_bm PIN5_bm /* e.g. PF5: check your board */

static uint8_t boot_count EEMEM;

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);

    uint8_t n = eeprom_read_byte(&boot_count);
    if (n == 0xFF) {
        n = 0;
    }
    n++;
    eeprom_update_byte(&boot_count, n);

    PORTF.DIRSET = LED_bm;
    for (;;) {
        for (uint8_t i = 0; i < n; i++) {
            PORTF.OUTSET = LED_bm;
            _delay_ms(150);
            PORTF.OUTCLR = LED_bm;
            _delay_ms(150);
        }
        _delay_ms(1000);
    }
}
