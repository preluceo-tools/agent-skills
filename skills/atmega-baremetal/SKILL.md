---
name: atmega-baremetal
description: Write bare-metal C firmware for ATmega microcontrollers with avr-gcc and avr-libc, using datasheet register names and no Arduino framework. Covers GPIO, clock and F_CPU, timers and PWM, USART, ADC, external and pin-change interrupts, ISR and atomic rules, sleep, watchdog, SPI, TWI, EEPROM and PROGMEM; writes a portable Makefile (build, size, hex, flash), or a no-framework PlatformIO project when the user builds with PlatformIO, and, for ATmega328P and ATmega2560, Wokwi and simulator project files. Use for register-level AVR code, flashing over ISP or UPDI, clock and fuse questions, or porting an existing Arduino sketch to bare metal. Chips - ATmega328P, 2560, 4809/4808/3208, 328PB, 1284P, 32U4, 168, 8A. Do NOT use to write a new Arduino sketch (setup/loop, digitalWrite, Serial), for Arduino IDE or library help, or for ARM, ESP32, PIC, ATtiny or XMEGA work.
license: 0BSD (examples and templates), CC-BY-4.0 (prose); see LICENSE and LICENSE-docs
metadata:
  version: "1.1.0"
---

# Bare-metal ATmega

## Hard rules

1. **Bare-metal only:** `main()`, avr-libc headers, datasheet register names. The Arduino framework never appears (`Arduino.h`, `setup()`, `loop()`, `digitalWrite`, `Serial.`, `Wire.h`, `SPI.h`). A request for a *new* Arduino sketch is out of scope: say so and offer the bare-metal equivalent. *Porting* an existing sketch to bare metal is in scope.
2. **Family gate first.** Name the target chip's family in the first line of every answer, before any warning or register code. Every recipe is family-specific and the two register models share almost nothing.
3. **Never write fuses or lock bits** unless the user asks. When a task touches the clock source, reset pin, debug, programming or flashing, warn about the fuse-brick hazards from `references/hazards.md`. When you give a fuse command, say which clock source and which `CKDIV8` setting it selects, and that `RSTDISBL`, `SPIEN` and `DWEN` are the bits only high-voltage programming can undo.
4. **Anything a reference marks "unverified" stays "unverified"** in your answer. Do not turn it into a fact.
5. **`F_CPU` must be set, must equal the real clock, and you state that clock.** A fresh Classic part runs at 1 MHz, not 8 MHz (`CKDIV8` is programmed); a 0-series part resets with `CLK_PER = CLK_MAIN / 6`. Correct a user who says "8 MHz internal RC" about a fresh part.

## Workflow

1. **Family gate.** Identify the chip (a board name maps to a chip: Uno/Nano = ATmega328P, Mega 2560 = ATmega2560, Nano Every/Uno WiFi Rev2 = ATmega4809, Leonardo/Micro = ATmega32U4). If the chip is unclear, ask. Then state one line, e.g. `Family gate: ATmega328P is Classic AVR (DDRx/PORTx/PINx, ISP).`

   | Family | Chips | Registers | Programming |
   |---|---|---|---|
   | Classic AVR | 328P, 2560, 328PB, 1284P, 32U4, 168, 8A | `DDRx`/`PORTx`/`PINx`, `TCCR1A`, `UBRR0` | ISP |
   | megaAVR 0-series | 4809, 4808, 3208 | `PORTx.DIR`, `TCA0.SINGLE`, `USARTn.BAUD`, CCP-protected | UPDI |

   Any other chip (ATtiny, XMEGA, AVR Dx, non-AVR): say it is outside this skill.
2. **Chip support.** Read `references/classic/chips.md` or `references/megaavr0/chips.md`. First-class chips (328P, 2560, 4809) get full recipes; 328PB, 1284P, 32U4, 168 are differences-table chips (write as the nearest first-class chip, then apply the row); 8A is warn-only (say so, list the traps, do not write full code).
3. **Toolchain.** Floor: avr-gcc >= 10 with avr-libc >= 2.2.0 (`avr-gcc --version`). Older toolchains: read `references/toolchain.md`.
4. **Write the project folder** (flat; see below). Copy `templates/Makefile`, set `MCU` and `F_CPU`. If a `platformio.ini` exists or the user builds with PlatformIO, read `references/platformio.md` instead and write no Makefile. For each peripheral, read its reference, then start from the matching compiled example.
5. **Simulator files for every simulatable chip (ATmega328P, ATmega2560), including a bare chip on a breadboard.** Read `references/simulation.md` and copy the templates. For any other chip say plainly that no supported simulator exists and emit none of `wokwi.toml`, `diagram.json`, `metadata.json`.
6. **Build and check.** Run `make` (`mingw32-make` on Windows). Confirm `firmware.hex` is at the project top level. If no toolchain is available, say the code was not compiled. Never claim it ran on hardware.
7. **Report:** the family gate, what compiled, what is unverified, and any fuse or clock hazard that applies.

## Project folder

```
main.c            (+ extra .c/.h beside it; or src/ with SRC set in the Makefile)
Makefile          from templates/Makefile
firmware.hex      built here, not in build/
build/            objects, firmware.elf
wokwi.toml  diagram.json  metadata.json    simulatable chips only
```

## Which reference

| Topic | Tier | Read (`<fam>` = `classic` or `megaavr0`) | Example (`examples/<fam>/`) |
|---|---|---|---|
| GPIO; clock and `F_CPU` | 1 | `references/<fam>/gpio-clock.md` | `gpio.c`, `clock.c` |
| Timers and PWM | 1 | `references/<fam>/timers-pwm.md` | `timers-pwm.c` |
| USART | 1 | `references/<fam>/usart.md` | `usart.c` |
| ADC | 1 | `references/<fam>/adc.md` | `adc.c` |
| External and pin-change interrupts; ISR and atomic rules | 1 | `references/<fam>/interrupts-isr.md` | `ext-pcint.c`, `isr-atomic.c` |
| Sleep and power; watchdog | 1 | `references/<fam>/sleep-power-watchdog.md` | `sleep-power.c`, `watchdog.c` |
| SPI, TWI | 2 | `references/<fam>/spi-twi.md` | `spi.c`, `twi.c` |
| EEPROM, PROGMEM and flash tables | 2 | `references/<fam>/eeprom-progmem.md` | `eeprom.c`, `progmem.c` |
| Fuses, lock bits, bootloader, extended flash, 32U4 USB, Event System and CCL, on-chip debug | 3 | `references/hazards.md` (hazards and datasheet pointer only: write no code) | none |
| Build, flash, older toolchain | | `references/toolchain.md` | |
| PlatformIO project (`platformio.ini`) | | `references/platformio.md` | |

Examples target the ATmega328P (Classic, also compile for the 2560) and the ATmega4809 (0-series). Their pin choices are examples: confirm them against the user's board.

## Porting an Arduino sketch

A port is a project like any other: workflow steps 4-7 apply, including the simulator files for a simulatable chip. Map pins to port bits (Uno: D0-D7 = PD0-PD7, D8-D13 = PB0-PB5, A0-A5 = PC0-PC5; other boards: look up the schematic). `Serial` becomes a USART setup; `analogWrite` a timer PWM; `delay()` `_delay_ms()` with a constant argument. `millis()` is a Timer0 overflow counter (1.024 ms at 16 MHz): name the timer your tick uses and say why it does not clash with the sketch's PWM. A Nano Every is a 0-series chip: that port is a rewrite, not a rename.

## Gotchas

Traps that bite before the topic reference is opened; the references hold the rest.


- `PINx = _BV(n)` toggles `PORTx` (not on ATmega8/8A) and compiles to `out`, not `sbi`. On the 0-series use `PORTx.OUTTGL`.
- ATmega328PB is not a drop-in for the 328P: `PRR` becomes `PRR0/PRR1`, `UBRR0/1`, `SPCR0/1`, `TWBR0/1`. ATmega32U4 has only `UBRR1`.
- Classic interrupt flags mostly clear when the vector is taken; 0-series flags do not (write 1 to `INTFLAGS`). `TWINT` never clears itself.
- On the 0-series never `#define BAUD`: it breaks `USART0.BAUD`.
- A misspelled `ISR()` vector name silently builds an unwired function; with `-Wall -Werror` it is an error. Vector names differ per chip (`USART_RX_vect` on the 328P, `USART0_RX_vect` on the 2560, `USART0_RXC_vect` on the 4809).
- `volatile` does not make a 16- or 32-bit access atomic: `ATOMIC_BLOCK` needs `-std=gnu99` or later.

## Done when

The family gate is stated; the project folder matches the layout; the code compiles with `-Wall -Wextra` for the target chip (or you said it was not compiled); no Arduino token appears; `F_CPU` is set; simulator files exist only for a simulatable chip; fuse hazards were warned about where relevant; unverified items are labelled.
