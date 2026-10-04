# PlatformIO projects

Read this when the project has a `platformio.ini`, or the user says they build with PlatformIO (e.g. in VS Code). It replaces workflow step 4 (Makefile) and the `firmware.hex` location in step 6; every other rule and reference applies unchanged. Write no `Makefile` into a PlatformIO project unless the user asks for one.

## Verified and unverified

- **Verified by building** (PlatformIO Core, platform `atmelavr`, board `uno`): the bare-metal project below compiles and links; `firmware.hex` and `firmware.elf` appear in `.pio/build/<env>/`; PlatformIO passes `-mmcu=atmega328p -DF_CPU=16000000L -Os` itself; `[platformio] src_dir = .` builds a flat `main.c`. The `atmelavr` toolchain checked was avr-gcc 7.3.0, so the Makefile's "avr-gcc >= 10" floor does not apply to Classic chips built this way.
- **From the PlatformIO documentation, not run:** the `fuses` and `bootloader` targets, `board_fuses.*`, `upload_protocol` values, `board_build.f_cpu`.
- **Unverified:** a bare-metal (no framework) ATmega4809 build on platform `atmelmegaavr`. The documentation lists only the Arduino framework for it and the platform could not be installed to test. For a 0-series chip say so, and offer the Makefile path (`references/toolchain.md`) as the supported one.

## Project

```
platformio.ini
src/main.c            (+ extra .c/.h beside it)
.pio/build/<env>/firmware.hex   built here
```

```ini
[env:uno]
platform = atmelavr
board = uno
; no "framework" line: that is what makes it bare metal
board_build.f_cpu = 16000000L
build_flags = -std=gnu11 -Wall -Wextra
upload_protocol = usbasp
```

- **Never add `framework = arduino`.** An existing project that has it is a *port* (SKILL.md, "Porting an Arduino sketch"): delete the line, move the code to `src/main.c`, drop `lib_deps` that need the Arduino core.
- **Do not define `F_CPU` in source.** PlatformIO passes `-DF_CPU` from `board_build.f_cpu`; the board file's default (16 MHz for an Uno) is a board fact, not the chip's fuse state. `F_CPU` must still equal the real clock: a fresh chip runs at 1 MHz (`CKDIV8`), and nothing in `platformio.ini` changes that unless the fuses are written.
- `-std=gnu11` keeps `ATOMIC_BLOCK` working, as in the Makefile.
- A flat layout is possible with `[platformio]` / `src_dir = .`; prefer `src/`.
- Build `pio run`, flash `pio run -t upload`, from the project folder. In VS Code these are the PlatformIO toolbar's Build and Upload.

## Fuse hazard

PlatformIO has two targets that write fuses: `pio run -t fuses` (reads `board_fuses.lfuse`, `hfuse`, `efuse`) and `pio run -t bootloader` (burns a bootloader and sets lock bits; whether it also writes fuses is unverified, so treat it as a fuse write). Third-party cores such as MiniCore and MegaCore can *generate* fuses from `board_build.f_cpu`, `board_hardware.oscillator` and `board_hardware.bod`, so an innocent-looking clock edit can become a clock-fuse write.

- Write no `board_fuses.*`, `board_bootloader.*` or `board_hardware.*` line unless the user asks.
- Never run or suggest `-t fuses` or `-t bootloader` unprompted. `-t upload` is the flash write.
- When you do give a fuse value, apply SKILL.md rule 3 in full: which clock source, which `CKDIV8`, and that `RSTDISBL`, `SPIEN` and `DWEN` are the bits only high-voltage programming can undo. Never copy a fuse set from a board definition.

## Simulator files

For a simulatable chip (ATmega328P, ATmega2560) keep `diagram.json` and `metadata.json` from `references/simulation.md`, and point `wokwi.toml` at the PlatformIO output:

```toml
[wokwi]
version = 1
firmware = '.pio/build/uno/firmware.hex'
elf = '.pio/build/uno/firmware.elf'
```

Use the environment name from `platformio.ini` in place of `uno`. Forward slashes only. The hex is only there after `pio run`.
