# megaAVR 0-series: pin interrupts, ISR and atomic rules

Examples: `examples/megaavr0/ext-pcint.c`, `examples/megaavr0/isr-atomic.c`.

## Pin interrupts

No `INTn`/`PCINTn` split. Each pin has a sense setting, `PORTx.PINnCTRL.ISC` (`PORT_ISC_RISING_gc`, `FALLING`, `BOTHEDGES`, `LEVEL`, `INPUT_DISABLE`), and each port has one vector: `PORTA_PORT_vect`, `PORTF_PORT_vect`... The ISR finds the pin from `PORTx.INTFLAGS`.

## Vector names

`TCA0_OVF_vect`, `TCA0_LUNF_vect`, `TCB0_INT_vect`, `USART0_RXC_vect`, `ADC0_RESRDY_vect`, `TWI0_TWIM_vect`, `PORTA_PORT_vect`, `RTC_CNT_vect`. Classic names such as `TIMER0_OVF_vect` build an ordinary unwired function and GCC warns (an error under `-Werror`).

## ISR rules

- **Flags are not cleared when the vector is taken.** "The interrupt request remains active until the Interrupt Flag is cleared": every ISR writes 1 to the matching `INTFLAGS` bit, or it re-enters forever. (Classic flags mostly auto-clear: do not carry that habit over.)
- Shared variables: `volatile`; `volatile` does not make a multi-byte access atomic: `ATOMIC_BLOCK(ATOMIC_RESTORESTATE)` from `<util/atomic.h>` (`-std=gnu99` or later).
