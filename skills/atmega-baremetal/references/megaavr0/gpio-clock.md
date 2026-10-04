# megaAVR 0-series: GPIO, clock and F_CPU

Examples: `examples/megaavr0/gpio.c`, `examples/megaavr0/clock.c`.

## GPIO

- `PORTx.DIR` / `DIRSET` / `DIRCLR` / `DIRTGL`, `PORTx.OUT` / `OUTSET` / `OUTCLR` / `OUTTGL`, `PORTx.IN`, per-pin `PORTx.PINnCTRL` (`PORT_PULLUPEN_bm`, `PORT_ISC_*`), `PORTx.INTFLAGS`. Use the `SET`/`CLR`/`TGL` registers instead of read-modify-write on `DIR`/`OUT`: each is one store.
- `VPORTx.DIR/OUT/IN/INTFLAGS` sit in I/O space 0x00-0x1F, so they compile to 1-cycle `sbi/cbi/out`. `PORTx.OUTTGL` is extended I/O: `sts`, 2 cycles. Writing `PORTx.IN` or `VPORTx.IN` also toggles `OUT`.
- `sbi/cbi` touch only the named bit, so they are safe on write-1-to-clear flags.
- Pull-up: `PORTx.PINnCTRL = PORT_PULLUPEN_bm`. Analog pins: `PORT_ISC_INPUT_DISABLE_gc`.
- 40-pin ATmega4809: see `chips.md` for the pins that must be disabled.

## Clock and F_CPU

- `F_CPU` must equal `CLK_PER`.
- **After reset `CLK_PER` is the main clock divided by 6.** Turn the prescaler off with `_PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);` and `F_CPU` equals OSC20M: 16 or 20 MHz as the `OSCCFG` fuse says. Every example does this first. `<avr/io.h>` documents `_PROTECTED_WRITE(reg, val)`.
- Configuration Change Protection (CCP): for protected registers (clock, WDT, reset-pin configuration) write the key to `CPU.CCP`, then the register within 4 instructions. A plain write is silently ignored.
