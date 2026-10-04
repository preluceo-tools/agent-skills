/* SPDX-License-Identifier: 0BSD */
/* Watchdog, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * MCUSR.WDRF survives a watchdog reset and keeps the watchdog enabled, so it is cleared and the
 * watchdog disabled in .init3, before main(). The loop then arms a 1 s timeout and feeds it.
 * Remove wdt_reset() to watch the chip reset.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/wdt.h>
#include <util/delay.h>

#if defined(__AVR_ATmega2560__)
#define LED_BIT PB7
#else
#define LED_BIT PB5
#endif

void wdt_early_off(void) __attribute__((naked, used, section(".init3")));
void wdt_early_off(void)
{
    MCUSR = 0;
    wdt_disable();
}

int main(void)
{
    DDRB |= _BV(LED_BIT);
    wdt_enable(WDTO_1S);
    for (;;) {
        PINB = _BV(LED_BIT);
        _delay_ms(200);
        wdt_reset();
    }
}
