/* SPDX-License-Identifier: 0BSD */
/* ISR and atomic rules, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * Timer0 overflow counts ticks; main() reads the 32-bit counter inside ATOMIC_BLOCK.
 * volatile alone does not make a multi-byte read atomic. ATOMIC_BLOCK needs -std=gnu99 or later.
 * 16 MHz / 64 / 256 = one overflow every 1.024 ms, so 488 overflows is about 0.5 s.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>

#if defined(__AVR_ATmega2560__)
#define LED_BIT PB7
#else
#define LED_BIT PB5
#endif

static volatile uint32_t ticks;

ISR(TIMER0_OVF_vect)
{
    ticks++;
}

static uint32_t ticks_now(void)
{
    uint32_t t;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        t = ticks;
    }
    return t;
}

int main(void)
{
    uint32_t last = 0;

    DDRB |= _BV(LED_BIT);
    TCCR0B = _BV(CS01) | _BV(CS00); /* clk/64 */
    TIMSK0 = _BV(TOIE0);
    sei();

    for (;;) {
        uint32_t now = ticks_now();
        if (now - last >= 488) {
            last = now;
            PINB = _BV(LED_BIT);
        }
    }
}
