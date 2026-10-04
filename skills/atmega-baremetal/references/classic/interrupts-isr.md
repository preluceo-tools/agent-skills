# Classic AVR: external and pin-change interrupts, ISR and atomic rules

Examples: `examples/classic/ext-pcint.c`, `examples/classic/isr-atomic.c`.

## External and pin-change interrupts

- `INTn`: `EICRA` (sense control) + `EIMSK` (enable). Pin-change: `PCICR` (group enable) + `PCMSKn` (per-pin mask); one vector per group (`PCINT0_vect`...). The INT0 pin differs by chip: PD2 on the ATmega328P, PD0 on the ATmega2560.

## Vector names

| Chip | Examples |
|---|---|
| ATmega328P | `TIMER0_OVF_vect`, `TIMER1_COMPA_vect`, `USART_RX_vect`, `ADC_vect`, `TWI_vect`, `INT0_vect`, `PCINT0_vect`, `WDT_vect` |
| ATmega328PB, 1284P | `USART0_RX_vect`, `USART1_RX_vect` |
| ATmega2560 | `USART0..3_RX_vect`, `TIMER5_OVF_vect` |
| ATmega32U4 | `USART1_RX_vect`, `USB_GEN_vect` |

The avr-libc manual's "What ISR names are available for my device?" FAQ is the full list.

## ISR rules

- `ISR(vect)` saves and restores `SREG` itself. Attributes: `ISR_BLOCK` (default), `ISR_NOBLOCK`, `ISR_NAKED`, `ISR_ALIASOF(vect)`; `EMPTY_INTERRUPT(vect)`. `SIGNAL()` and `SIG_*` names are deprecated.
- A **misspelled vector name builds an ordinary, unwired function**; GCC warns that the name "appears to be a misspelled" vector, which `-Wall -Werror` makes an error. An enabled interrupt with no handler jumps to the reset vector; define `ISR(BADISR_vect)` to catch it.
- Most flags clear automatically when the vector is taken. `RXC` clears by reading `UDRn`. **`TWINT` is never cleared by hardware.**
- Shared variables: `volatile`. `volatile` does **not** make a multi-byte access atomic: use `ATOMIC_BLOCK(ATOMIC_RESTORESTATE)` from `<util/atomic.h>` (needs `-std=gnu99` or later; the Makefile uses `-std=gnu11`). `break`/`continue` inside an `ATOMIC_BLOCK` need care because it is a `for` loop.
