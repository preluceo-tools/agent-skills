# Classic AVR: USART

Example: `examples/classic/usart.c`.

- Divisor: `UBRRn = F_CPU / (16 * BAUD) - 1` (normal) or `/ (8 * BAUD)` with `U2X`. Round with `((F_CPU + BAUD * 8) / (BAUD * 16) - 1)`.
- `<util/setbaud.h>` does this: define `F_CPU` (an integer, not a float) and `BAUD`, then include it. It gives `UBRR_VALUE`, `UBRRH_VALUE`, `UBRRL_VALUE`, `USE_2X`; `BAUD_TOL` defaults to 2 %. To re-include with another `BAUD`, `#undef BAUD` first. It does not apply to the 0-series.
- Registers: `UCSRnA` (`UDREn`, `RXCn`, `U2Xn`), `UCSRnB` (`TXENn`, `RXENn`, `RXCIEn`), `UCSRnC` (frame format), `UDRn`.
- Names by chip:

| Chip | Registers | RX vector |
|---|---|---|
| ATmega328P | `UBRR0`, `UCSR0x`, `UDR0` | `USART_RX_vect` |
| ATmega328PB, 1284P | `UBRR0`, `UBRR1` | `USART0_RX_vect`, `USART1_RX_vect` |
| ATmega2560 | `UBRR0`..`UBRR3` | `USART0_RX_vect`..`USART3_RX_vect` |
| ATmega32U4 | **`UBRR1` only** (`UBRR0` is undefined) | `USART1_RX_vect` |
| ATmega8/8A | unindexed `UBRRH/UBRRL/UCSRA..C`, `URSEL` bit | warn-only chip |

- `RXC` is cleared by reading `UDRn`.
