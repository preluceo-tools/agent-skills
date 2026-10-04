# Simulation and simulator project files

## Which chips

**Simulatable: ATmega328P and ATmega2560 only.** For every other chip say plainly that no supported simulator exists and emit no simulator files. In particular:

- **ATmega4809/4808/3208: no simulator.** Wokwi closed the request "Not planned"; simavr's request is open; Proteus and SimulIDE do not list it.
- **ATmega32U4, 328PB, 1284P, 168, 8A:** not on Wokwi (32U4 "Not planned"). Never run a 328PB hex on Wokwi's Uno part: USART1, SPI1, TWI1 and Timer3/4 are silently missing.
- One line is allowed: simavr (GPL-3) covers more Classic chips (not the 4809); on Windows it needs WSL/Docker. Generate no files for it.

## Files for a simulatable chip

The Makefile writes `firmware.hex` at the project top level and `build/firmware.elf`. Copy from `templates/`:

| File | Source | Notes |
|---|---|---|
| `wokwi.toml` | `templates/wokwi.toml` | `[wokwi]`, `version = 1`, `firmware = 'firmware.hex'`, `elf = 'build/firmware.elf'`. Forward slashes only. `elf` is optional (GDB, sometimes faster). |
| `diagram.json` | `templates/diagram/uno.json` (ATmega328P Uno), `nano.json`, `mega.json` (ATmega2560) | Wokwi tuple format. Board part is `wokwi-arduino-uno`, `wokwi-arduino-nano` or `wokwi-arduino-mega`. |
| `metadata.json` | `templates/metadata/uno.json` or `mega.json` | Playground file: `board` `uno` or `mega`, `category` `bare-metal`. **Unverified:** its full schema is not in the source material; emit only these two keys. |

Edit the copied `diagram.json` to match the circuit: pin names are **Arduino numbers, not port bits** (PB5 = `"13"`, PB0 = `"8"`, PD0 = `"0"`, PC0 = `"A0"` on the Uno; Mega `0`..`53`, `A0`..`A15`). The template wires pin 13 through a 220 Ohm resistor to an LED. Do not emit `sketch.ino` or `libraries.txt`. Run `@wokwi/diagram-lint` if available; note it does **not** flag a wrong `board-*` part type, so double-check the board type is exactly one of the three above.

Part types: `wokwi-led` (pins `A`, `C`), `wokwi-resistor` (`1`, `2`; attr `value`), `wokwi-pushbutton` (`1.l`, `1.r`, `2.l`, `2.r`), `wokwi-potentiometer`, `wokwi-buzzer`, `wokwi-servo`, `wokwi-lcd1602`, `wokwi-ssd1306`, `wokwi-neopixel`, `wokwi-gnd`, `wokwi-vcc`. The serial monitor is not a part: it is `$serialMonitor` (`TX`/`RX`) inside `connections`. Uno `3.3V`, `IOREF`, `AREF`, `RESET` are unavailable in the simulation.

## Pitfalls

1. **Simulated clock must equal `F_CPU`.** Wokwi: the board's `frequency` attribute (`"16m"` default, also `"8m"`, `"20m"`); avr8js: the Hz you pass; simavr: `-f`.
2. **Silent divergences** (the simulator keeps running; hardware would not): SLEEP is a no-op; SPM is a no-op; no fuse model (`CKDIV8`, brown-out, `BOOTSZ` have no effect, so real timing can be 8x slower); partial reset (a watchdog reset re-enters `main` with stale I/O state); no timer input capture; no Timer2 async mode; SPI and TWI master only; no analog comparator; ATmega2560 has no Wokwi input capture or output compare modulator.
3. No bootloader: execution starts at `__vectors`; the hex must start at address 0.
4. Wokwi's serial monitor shows only after the first byte; `"serialMonitor": {"display": "always"}` (already in the templates) shows it from the start.
5. Wokwi EEPROM is blank (0xFF) each run.
6. Interrupt re-entry with a held flag differs from silicon (reported wokwi-features#924).
7. **avr8js does not model internal pull-ups:** an undriven input reads 0 until the host calls `setPin()`. Observed with avr8js 0.21.1; a button released through a pull-up needs the host to drive the pin high. Wokwi's pushbutton part drives the pin.

## How the user runs it

- **Wokwi VS Code extension:** open the folder with `wokwi.toml` and `diagram.json`, build first (Wokwi does not compile), F1 > "Wokwi: Start Simulator". Needs a free license: a renewable 30-day personal license, free for open-source projects; commercial use needs a purchased license. It requires an internet connection.
- **Wokwi CLI / CI:** needs a CI token from the Wokwi dashboard (the CLI docs name the environment variable) and runs in the cloud with monthly minute caps; not an offline test runner. `wokwi-cli` automation docs show `expected:` for `expect-pin` but the source reads `value:`.
- **Wokwi web editor:** cannot compile a plain `main.c` (it builds `sketch.ino` through the Arduino CLI). Loading a prebuilt hex via F1 > "Load HEX File and Start Simulation..." rests on a 2021 maintainer comment: **unverified**, not in current docs.
- **Free-tier use on a private repository** is ambiguous in Wokwi's terms (the web service is personal and non-commercial; the extension is for open-source projects or a personal 30-day license).
- **avr8js headless** (free, offline, 328P presets only): a JS program loads `firmware.hex` with an Intel-HEX parser, creates `new CPU(flash, 2048)` (the default SRAM is 8192, wrong for a 328P), and runs `avrInstruction(cpu); cpu.tick();` in a loop; **`cpu.tick()` after every instruction is mandatory**. The 2560 and 4809 have no avr8js presets.
