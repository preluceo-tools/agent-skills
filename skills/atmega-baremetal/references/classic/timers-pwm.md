# Classic AVR: timers and PWM

Examples: `examples/classic/timers-pwm.c`, `examples/classic/isr-atomic.c` (Timer0 overflow tick).

- Timer0 and Timer2 are 8-bit: `TCCRnA/B`, `TCNTn`, `OCRnx`, `TIMSKn`, `TIFRn`. Timer1 (plus 3/4/5 on the 2560) is 16-bit: `TCCR1A/B/C`, `TCNT1`, `ICR1`, `OCR1A/B`.
- PWM modes: fast PWM, phase-correct, phase-and-frequency-correct, CTC, custom TOP (via `ICR1` or `OCR1A`). Mode bits are split across `WGMn0..3` in `TCCRnA/B`.
- Output-compare pins differ by chip: OC1A is PB1 on the ATmega328P and PB5 on the ATmega2560.
- **16-bit registers share one TEMP byte.** Write the high byte first, then the low; read the low first, then the high. If an ISR also touches a 16-bit timer register, wrap main-line access in `ATOMIC_BLOCK`. The compiler handles the order for `OCR1A = x;`; the hazard is the ISR.
- Input capture: Timer1 `ICP1` is PB0 on the ATmega328P; simulators do not model it (`../simulation.md`).
- A tick for timekeeping: at 16 MHz, Timer0 with /64 overflows every 1.024 ms (64 x 256 cycles).
