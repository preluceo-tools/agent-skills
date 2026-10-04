# Classic AVR: SPI and TWI (Tier 2)

Examples: `examples/classic/spi.c`, `examples/classic/twi.c`.

## SPI

- `SPCR` (`SPE`, `MSTR`, `CPOL`, `CPHA`, `SPR1:0`), `SPSR` (`SPIF`, `SPI2X`), `SPDR`. Master transfer: write `SPDR`, wait for `SPIF`, read `SPDR`.
- The SPI pins are fixed per chip: PB2-PB5 on the ATmega328P (SS, MOSI, MISO, SCK), PB0-PB3 on the ATmega2560 (datasheet pinouts; not in the validated research). Set MOSI, SCK and SS to output.
- In master mode keep SS an output, or a low level on it switches the module to slave.
- ATmega328PB: `SPCR0/SPCR1`.
- ISP shares these pins: see `../hazards.md`.
- Simulators model SPI master only.

## TWI (I2C)

- `TWBR`, `TWSR` (prescaler, status), `TWCR`, `TWDR`. SCL = F_CPU / (16 + 2 * TWBR * prescaler): the datasheet formula, not in the validated research.
- `<util/twi.h>` provides the status codes (`TW_START`, `TW_MT_SLA_ACK`, `TW_MT_DATA_ACK`, `TW_STATUS`...).
- **`TWINT` is never cleared by hardware**: write 1 to it to start each step. Every wait needs a timeout; without bus pull-ups it never ends.
