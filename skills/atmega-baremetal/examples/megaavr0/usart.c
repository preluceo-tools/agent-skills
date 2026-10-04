/* SPDX-License-Identifier: 0BSD */
/* USART0, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * Prints "Hello" every 500 ms at 9600 8N1 and echoes any received byte. <util/setbaud.h> does not
 * apply here: BAUD = 64 * f_CLK_PER / (S * f_baud), S = 16 in normal mode, valid 64..65535.
 * Default mux: TX on PA0, RX on PA1 (check the datasheet for your package).
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

#define BAUD_RATE 9600UL
/* 64 * F_CPU / (16 * baud) = 4 * F_CPU / baud, rounded */
#define USART_BAUD_VALUE ((uint16_t)(((uint32_t)F_CPU * 4UL + BAUD_RATE / 2UL) / BAUD_RATE))

static void uart_init(void)
{
    PORTA.DIRSET = PIN0_bm; /* TX out */
    PORTA.DIRCLR = PIN1_bm; /* RX in */
    USART0.BAUD = USART_BAUD_VALUE;
    USART0.CTRLB = USART_TXEN_bm | USART_RXEN_bm; /* reset CTRLC is async 8N1 */
}

static void uart_putc(char c)
{
    while (!(USART0.STATUS & USART_DREIF_bm)) { }
    USART0.TXDATAL = (uint8_t)c;
}

static void uart_puts(const char *s)
{
    while (*s) {
        uart_putc(*s++);
    }
}

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);
    uart_init();
    for (;;) {
        uart_puts("Hello\r\n");
        if (USART0.STATUS & USART_RXCIF_bm) {
            uart_putc((char)USART0.RXDATAL); /* reading RXDATAL clears RXCIF */
        }
        _delay_ms(500);
    }
}
