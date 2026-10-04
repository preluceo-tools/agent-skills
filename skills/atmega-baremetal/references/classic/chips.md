# Classic AVR chips

Family: `DDRx`/`PORTx`/`PINx` registers, ISP programming.

## First-class chips (full recipes, compiled examples)

| | ATmega328P | ATmega2560 |
|---|---|---|
| Flash / SRAM / EEPROM | 32 KB / 2 KB / 1 KB | 256 KB / 8 KB / 4 KB |
| I/O lines | not covered by the validated research | **86** (54 is the Arduino Mega *board's* digital pin count) |
| Max clock | 20 MHz at 4.5-5.5 V, 10 MHz at 2.7 V, 4 MHz at 1.8 V, linear between. 16 MHz needs about 3.8 V (derived). | 16 MHz at 4.5-5.5 V only (2560V: 8 MHz at 2.7 V) |
| USART | USART0: `UBRR0`, `UCSR0A/B/C`, `UDR0`, `USART_RX_vect` | USART0-3: `UBRR0..3`, `USART0_RX_vect` ... `USART3_RX_vect` |
| Power reduction | `PRR` | `PRR0`, `PRR1` |
| Timers | 0, 1, 2 | 0-5 (`TIMER5_OVF_vect`) |
| Debug | debugWIRE (`DWEN` fuse, hijacks RESET) | JTAG on PF4-PF7 (shared with ADC4-7) |
| Boards | Uno R3, Nano, Pro Mini | Arduino Mega 2560 |
| Simulatable | yes (Wokwi Uno/Nano, avr8js) | yes (Wokwi Mega) |

ATmega2560 extras: flash above 64 KB needs `RAMPZ`/`ELPM` and the `pgm_read_*_far` family; the PC is 24-bit (`EIND`); function pointers beyond 128 KiB need `-mrelax` at link. Read `eeprom-progmem.md`.

Pin names differ between the two chips (OC1A is PB1 on the 328P, PB5 on the 2560; INT0 is PD2 vs PD0; SPI is PB2-5 vs PB0-3). The compiled examples switch on `__AVR_ATmega2560__`. Arduino pin 13 is PB5 on Uno-style boards and PB7 on the Mega (the Mega mapping is not in the validated research: confirm against the board schematic).

## Differences-table chips (write the code as for the nearest first-class chip, then apply the row)

| Chip | Differences from ATmega328P |
|---|---|
| ATmega328PB | **Not a drop-in.** Second instances are renamed `SPCR0/1`, `TWBR0/1`, `UBRR0/1`; `PRR` is split into `PRR0/PRR1` (`PRR` does not compile); vectors `USART0_RX_vect`, `USART1_RX_vect`. Three 16-bit timers, two USARTs, two SPI, two TWI, 10 PWM channels, 27 I/O. 20 MHz at 4.5-5.5 V. Microchip publishes "Differences between ATmega328P and ATmega328PB" (AT15007): unverified, not read. Not simulatable: never run it on Wokwi's Uno part (USART1, SPI1, TWI1, Timer3/4 silently missing). |
| ATmega1284P | 128 KB flash, 16 KB SRAM, 4 KB EEPROM, 32 I/O, two USARTs (`UBRR0/1`, `USART0_RX_vect`). JTAG on PC2-PC5. 0-20 MHz at 4.5-5.5 V. Far-flash rules as the 2560. The datasheet's fuse table lists a `DWEN` bit though the debug chapter documents JTAG only: meaning unresolved. Not simulatable. |
| ATmega32U4 | 32 KB flash, **2.5 KB** SRAM, 1 KB EEPROM, 26 I/O. **Only USART1**: `UBRR1`, `UCSR1B`, `USART1_RX_vect`; `UBRR0` does not exist. Full-speed USB device controller (6 endpoints, 832 B DPRAM); HID is firmware, not hardware. 8 MHz at 2.7 V, 16 MHz at 4.5 V. JTAG. Boards: Leonardo, Micro, Pro Micro. Not simulatable (Wokwi "not planned"; Microchip Studio "never"). USB is Tier 3: read `../hazards.md`. |
| ATmega168 | 16 KB flash. Documented in the 48/88/168/328 datasheet (168A/PA; plain non-A 168 not read). debugWIRE. Not simulatable. |

## Warn-only chip

**ATmega8A** (8 KB flash, 1 KB SRAM, 0-16 MHz): say the skill does not write full code for it, then list the traps so the user can proceed: own datasheet; unindexed `UBRRH/UBRRL/UCSRA..C` with the `URSEL` bit shared between `UCSRC` and `UBRRH`; **no `PINx` toggle** (`PINx` is read-only); no `PRR`; `rjmp` vector table; ISP and HVPP only (no on-chip debug).
