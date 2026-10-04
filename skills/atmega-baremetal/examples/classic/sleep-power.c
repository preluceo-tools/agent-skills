/* SPDX-License-Identifier: 0BSD */
/* Sleep and power reduction, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * Timer1 compare interrupt wakes the CPU from idle sleep twice a second; main() toggles the LED.
 * The cli / test flag / sleep_enable / sei / sleep_cpu order cannot lose a wake-up:
 * the instruction after sei() runs before any interrupt is taken.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/power.h>
#include <avr/sleep.h>

#if defined(__AVR_ATmega2560__)
#define LED_BIT PB7
#else
#define LED_BIT PB5
#endif

static volatile uint8_t tick;

ISR(TIMER1_COMPA_vect)
{
    tick = 1;
}

int main(void)
{
    DDRB |= _BV(LED_BIT);
    power_adc_disable(); /* PRR macros; the 0-series has no PRR */
    power_spi_disable();
    power_twi_disable();

    TCCR1B = _BV(WGM12) | _BV(CS12) | _BV(CS10); /* CTC, clk/1024 */
    OCR1A = (F_CPU / 1024UL / 2UL) - 1UL;        /* 2 Hz */
    TIMSK1 = _BV(OCIE1A);
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
            PINB = _BV(LED_BIT);
        }
    }
}
