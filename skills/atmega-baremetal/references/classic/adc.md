# Classic AVR: ADC

Example: `examples/classic/adc.c`.

- `ADMUX`: reference (`REFS1:0`), result alignment, channel. `ADCSRA`: `ADEN`, `ADSC`, `ADATE` (auto-trigger), `ADIF`, `ADIE`, `ADPS2:0` (prescaler). `ADCSRB`: auto-trigger source. Result in `ADC` (or `ADCL/ADCH`).
- Single conversion: set `ADSC`, wait until it clears, read `ADC`. Interrupt-driven: `ADIE` + `ISR(ADC_vect)`.
- Prescaler: pick it so the ADC clock stays in the datasheet's range for full resolution (the example uses /128 at 16 MHz = 125 kHz; the exact range is not in the validated research, check the datasheet for your chip).
- Channels map to different pins per chip (ADC0 is PC0 on the ATmega328P, PF0 on the ATmega2560). The ATmega2560's channels 8-15 need `MUX5` in `ADCSRB` (datasheet pinout; not in the validated research).
- Simulators: Wokwi and avr8js model the ADC; the analog comparator is not modelled.
