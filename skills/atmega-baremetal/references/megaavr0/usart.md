# megaAVR 0-series: USART

Example: `examples/megaavr0/usart.c`.

- `USARTn.BAUD = 64 * f_CLK_PER / (S * f_baud)`, S = 16 normal, 8 double-speed, 2 synchronous. Valid range 64..65535. For S = 16 this is `4 * F_CPU / baud`. `<util/setbaud.h>` does not apply.
- Registers: `CTRLA`, `CTRLB` (`TXEN`, `RXEN`), `CTRLC` (frame format; the reset value is asynchronous 8N1), `STATUS` (`DREIF`, `RXCIF`, `TXCIF`), `TXDATAL`, `RXDATAL`.
- **Never `#define BAUD`** (or `BAUD` as any macro): `USARTn.BAUD` is a struct member, so the macro breaks the build (`expected identifier before numeric constant`). The example uses `BAUD_RATE`.
- Four instances, `USART0..3`; vectors `USARTn_RXC_vect`, `USARTn_DRE_vect`, `USARTn_TXC_vect`. Reading `RXDATAL` clears `RXCIF`.
- Set the TX pin `DIR` to output yourself; the port multiplexer chooses the pins (USART0 default PA0/PA1: check the datasheet for your package).
- Remember `CLK_PER` is /6 after reset: run the clock step first (`gpio-clock.md`) or the baud is 6x off.
