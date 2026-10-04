/* SPDX-License-Identifier: 0BSD */
/* SPI0 host, megaAVR 0-series. Targets ATmega4809 (also 4808 and 3208).
 * Sends one byte every 10 ms with a manual chip select. Default mux pins PA4 MOSI, PA5 MISO,
 * PA6 SCK, PA7 SS come from the datasheet pinout, not the validated research: check them.
 * SSD makes the SS pin ignored by the module, so a manual chip select cannot flip it to client mode.
 * Build: make MCU=atmega4809 F_CPU=16000000UL */
#include <avr/io.h>
#include <util/delay.h>

#define CS_bm PIN7_bm

static uint8_t spi_xfer(uint8_t b)
{
    SPI0.DATA = b;
    while (!(SPI0.INTFLAGS & SPI_IF_bm)) { }
    return SPI0.DATA;
}

int main(void)
{
    _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);

    PORTA.OUTSET = CS_bm; /* chip select idles high */
    PORTA.DIRSET = PIN4_bm | PIN6_bm | CS_bm;
    SPI0.CTRLB = SPI_SSD_bm | SPI_MODE_0_gc;
    SPI0.CTRLA = SPI_MASTER_bm | SPI_PRESC_DIV16_gc | SPI_ENABLE_bm;

    for (;;) {
        PORTA.OUTCLR = CS_bm;
        (void)spi_xfer(0xA5);
        PORTA.OUTSET = CS_bm;
        _delay_ms(10);
    }
}
