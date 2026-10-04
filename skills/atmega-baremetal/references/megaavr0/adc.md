# megaAVR 0-series: ADC

Example: `examples/megaavr0/adc.c`.

- `ADC0.CTRLA` (`ENABLE`, `FREERUN`, `RESSEL`) through `CTRLE`, `CTRLC` (`PRESC`, `REFSEL`), `MUXPOS`, `COMMAND` (`ADC_STCONV_bm` starts a conversion), `RES`, `INTFLAGS` (`RESRDY`).
- ADC clock must be 50 kHz to 1.5 MHz for full resolution: pick `PRESC` from `CLK_PER`.
- Single conversion: set `MUXPOS`, write `COMMAND`, wait for `RESRDY`, read `RES` (reading it clears the flag).
- Interrupt: `ISR(ADC0_RESRDY_vect)`; write 1 to `INTFLAGS`.
