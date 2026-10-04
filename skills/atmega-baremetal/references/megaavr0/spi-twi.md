# megaAVR 0-series: SPI and TWI (Tier 2)

Examples: `examples/megaavr0/spi.c`, `examples/megaavr0/twi.c`.

## SPI0

- `SPI0.CTRLA` (`MASTER`, `PRESC`, `ENABLE`), `CTRLB` (`SSD`, mode), `INTCTRL`, `INTFLAGS` (`IF`), `DATA`. Transfer: write `DATA`, wait for `INTFLAGS.IF`, read `DATA`.
- Default pins PA4 MOSI, PA5 MISO, PA6 SCK, PA7 SS (datasheet pinout; not in the validated research).
- `SSD` stops the SS pin from affecting the module, so a manual chip select cannot flip it to client mode.

## TWI0

- Host registers: `TWI0.MCTRLA` (`ENABLE`), `MCTRLB` (`MCMD`: stop etc.), `MSTATUS` (`WIF`, `RIF`, `RXACK`, `BUSSTATE`), `MBAUD`, `MADDR`, `MDATA`. Writing `MADDR` sends START and the address.
- `MBAUD` formula (datasheet: f_SCL = f_CLK_PER / (10 + 2 * BAUD + f_CLK_PER * T_rise)) is **not in the validated research**; the example ignores `T_rise`: check it.
- `<util/twi.h>` status masks are for the Classic `TWSR` and do not apply.
- Every wait needs a timeout; without bus pull-ups it never ends.
