# Classic AVR: sleep, power reduction, watchdog

Examples: `examples/classic/sleep-power.c`, `examples/classic/watchdog.c`.

## Sleep

- `SMCR` (`SE`, `SM2:0`) selects one of six modes: idle, ADC noise reduction, power-save, power-down, standby, extended standby. `<avr/sleep.h>`: `set_sleep_mode()`, `sleep_enable()`, `sleep_cpu()`, `sleep_disable()`, `sleep_mode()`, `sleep_bod_disable()`.
- **Lost wake-up:** `cli(); if (!flag) { sleep_enable(); sei(); sleep_cpu(); sleep_disable(); } sei();`. The instruction after `sei()` runs before an interrupt is taken, so the interrupt cannot slip in between the test and the sleep.
- Typical power-down current is 0.1 uA (power-save 0.75 uA with the 32 kHz RTC) at 1.8 V, 25 C, from the ATmega328P datasheet. Which interrupts can wake each mode is **not in the validated research**: read the datasheet's sleep-mode table before choosing power-down.

## Power reduction

`PRR` on the ATmega328P; `PRR0`/`PRR1` on the 328PB, 1284P, 2560 and 32U4; none on the ATmega8/8A. `<avr/power.h>`: `power_adc_disable()`, `power_spi_disable()`, `power_twi_disable()`, `power_timer0_disable()`... `PRR` does not compile on the 328PB.

## Watchdog

- `WDTCSR` needs the timed sequence (`WDCE` + `WDE`, then the new value within 4 cycles). `<avr/wdt.h>`: `wdt_enable(WDTO_xx)`, `wdt_reset()`, `wdt_disable()`.
- **`MCUSR.WDRF` persists across a watchdog reset.** Clear `MCUSR` and call `wdt_disable()` in `.init3`, before `main()`: the example shows the pattern.
- Software reset is the watchdog: `wdt_enable(WDTO_15MS); for (;;) {}`.
- Simulators: the watchdog is modelled, but `cpu.reset()` in avr8js does not restore I/O registers, so a watchdog reset re-enters `main` with stale peripheral state.
