# megaAVR 0-series: timers and PWM

Examples: `examples/megaavr0/timers-pwm.c`, `examples/megaavr0/isr-atomic.c` (TCA0 1 ms tick).

- **TCA0**: 16-bit, single mode or split mode (two 8-bit halves). Single-mode registers: `TCA0.SINGLE.CTRLA` (`CLKSEL`, `ENABLE`), `CTRLB` (`CMPnEN`, `WGMODE`), `PER`, `CMPn`, `CMPnBUF`, `INTCTRL`, `INTFLAGS`. PWM waveform modes: single-slope (`TCA_SINGLE_WGMODE_SINGLESLOPE_gc`), dual-slope, frequency.
- Write the duty to `CMPnBUF` to update at the period boundary without glitches.
- PWM output pin is set by the port multiplexer; WO0 is PA0 by default (check the datasheet for your package) and the pin's `DIR` bit must be set to output.
- **TCB0-3**: 16-bit, with one-shot, capture-on-event and PWM modes. There is no ICP pin: capture needs the Event System.
