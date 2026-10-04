# megaAVR 0-series: sleep, power, watchdog

Examples: `examples/megaavr0/sleep-power.c`, `examples/megaavr0/watchdog.c`.

## Sleep

- `SLPCTRL.CTRLA` (`SEN`, `SMODE`): idle, standby, power-down. `<avr/sleep.h>` handles it: `set_sleep_mode(SLEEP_MODE_IDLE)`, `sleep_enable()`, `sleep_cpu()`, `sleep_disable()`.
- Use the same lost-wake-up order as Classic AVR: `cli(); if (!flag) { sleep_enable(); sei(); sleep_cpu(); sleep_disable(); } sei();`.
- Which wake sources work in each mode is **not in the validated research**: read the datasheet before using power-down or standby. The example idles.

## Power reduction

**There is no `PRR` and no `power_*_disable()` macros** (`power_adc_disable` is undeclared on the 4809). Stop a peripheral through its own enable bit; `RUNSTDBY` bits decide what keeps running in standby. The event system and CCL can run without the CPU ("SleepWalking").

## Watchdog and reset

- `WDT.CTRLA` is CCP-protected. `<avr/wdt.h>` has a CCP branch for this family: `wdt_enable(WDTO_1S)`, `wdt_reset()`, `wdt_disable()`.
- There is no `MCUSR`/`WDRF`: the reset cause is `RSTCTRL.RSTFR` (write 1 to clear). `RSTCTRL.SWRR` is a software reset (whether it is CCP-protected is not in the validated research).
