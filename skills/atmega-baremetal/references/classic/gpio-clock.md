# Classic AVR: GPIO, clock and F_CPU

Examples: `examples/classic/gpio.c`, `examples/classic/clock.c`.

## GPIO

- `DDRx` bit 1 = output. `PORTx` = output level, or pull-up when the pin is an input. `PINx` = input level.
- Writing 1 to `PINx` toggles `PORTx` regardless of `DDRx`. Not on ATmega8/8A. It compiles to `ldi` + `out` (1 cycle), **not** `sbi`.
- `PORTB |= _BV(PB5)` compiles to one `sbi` (2 cycles on AVRe). `sbi/cbi/sbis/sbic` reach only I/O addresses 0x00-0x1F; extended I/O (above 0x3F) is `lds/sts` (2 cycles). At `-O0` the same statement is `ld/ori/st`: build with `-Os`.
- `DDRB = DDRD = 0xff` forces a read-back of the first register; write them as separate statements.

## Clock and F_CPU

- GCC does not set `F_CPU`; the Makefile passes `-DF_CPU=<Hz>UL`. It must equal the real clock, or `_delay_ms`, USART and TWI divisors are wrong.
- A fresh part runs the internal 8 MHz RC with `CKDIV8` programmed: 1 MHz. A crystal is optional, not required. Changing `CKDIV8` is a fuse write (see `../hazards.md`).
- `CLKPR`: write `CLKPCE`, then the new `CLKPS` within 4 cycles. `clock_prescale_set(clock_div_1)` from `<avr/power.h>` does it.
- `<util/delay.h>`: busy-wait, not a hardware timer. Needs `F_CPU` defined first (it falls back to 1 MHz with `#warning "F_CPU not defined"`; `-Werror` turns that into an error, which is wanted), a compile-time-constant argument and optimisation on.
