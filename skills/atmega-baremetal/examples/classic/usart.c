/* SPDX-License-Identifier: 0BSD */
/* USART0, Classic AVR. Targets ATmega328P; also compiles for ATmega2560.
 * Prints "Hello" every 500 ms at 9600 8N1 and echoes any received byte.
 * Baud divisor comes from <util/setbaud.h>: F_CPU (integer) and BAUD are defined before the include.
 * Build: make MCU=atmega328p F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

#define BAUD 9600
#include <util/setbaud.h>

static void uart_init(void)
{
    UBRR0H = UBRRH_VALUE;
    UBRR0L = UBRRL_VALUE;
#if USE_2X
    UCSR0A |= _BV(U2X0);
#else
    UCSR0A &= ~_BV(U2X0);
#endif
    UCSR0B = _BV(TXEN0) | _BV(RXEN0);
    UCSR0C = _BV(UCSZ01) | _BV(UCSZ00); /* 8 data bits, no parity, 1 stop */
}

static void uart_putc(char c)
{
    while (!(UCSR0A & _BV(UDRE0))) { }
    UDR0 = c;
}

static void uart_puts(const char *s)
{
    while (*s) {
        uart_putc(*s++);
    }
}

int main(void)
{
    uart_init();
    for (;;) {
        uart_puts("Hello\r\n");
        if (UCSR0A & _BV(RXC0)) {
            uart_putc((char)UDR0); /* reading UDR0 clears RXC0 */
        }
        _delay_ms(500);
    }
}
