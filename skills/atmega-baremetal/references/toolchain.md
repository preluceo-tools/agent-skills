# Toolchain and build

## Floor

Upstream **avr-gcc >= 10 with avr-libc >= 2.2.0**. GCC 10 added the megaAVR 0-series devices; avr-libc 2.2.0 (2024-06-08) shipped the first ATmega4809/4808/3208 headers.

**Older toolchain (Microchip AVR 8-bit GNU Toolchain, GCC 7.3 / avr-libc 2.0.0).** Plain `-mmcu=atmega4809` fails (`device-specs/specs-atmega4809: No such file`). Install the Microchip ATmega_DFP device pack and pass `-mmcu=atmega4809 -B <DFP>/gcc/dev/atmega4809 -isystem <DFP>/include`. Classic chips build with plain `-mmcu=` on the old toolchain. This is the only fallback the skill documents.

## The Makefile (`templates/Makefile`)

Targets: `build` (hex + size), `size`, `hex`, `flash`, `clean`. Variables: `MCU`, `F_CPU`, `SRC` (default `main.c`; set `SRC="main.c src/uart.c"` for more files), `TARGET`, `PROGRAMMER`, `PORT`, `AVRDUDE_FLAGS`, `EXTRA_CFLAGS`.

- `make hex MCU=atmega2560 F_CPU=16000000UL` writes `firmware.hex` at the project top level and `build/firmware.elf`.
- Flags: `-mmcu=<mcu> -DF_CPU=<Hz>UL -std=gnu11 -Os -g -Wall -Wextra -ffunction-sections -fdata-sections`, link `-Wl,--gc-sections`. `-std=gnu11` is needed for `ATOMIC_BLOCK`. Output `avr-objcopy -O ihex -R .eeprom`.
- **No Arduino include or library paths.** `Arduino.h`, `Wire.h`, `SPI.h` fail to compile; `pinMode` and `Serial` fail to link. Do not add them.

## Flashing (`make flash`)

`PROGRAMMER` and `PORT` are the user's: the defaults are `usbasp` (ISP, no `PORT` needed) for Classic AVR and `serialupdi` (needs `PORT`) for the 0-series. Part id is derived (`atmega328p` becomes `m328p`).

| Target | avrdude |
|---|---|
| Classic over ISP | `avrdude -c usbasp -p m328p -U flash:w:firmware.hex:i` |
| Classic, Arduino bootloader as transport only | `make flash PROGRAMMER=arduino PORT=<serial port> AVRDUDE_FLAGS="-b 115200 -D"` (Uno: protocol `arduino`, 115200; old Nano bootloader 57600) |
| ATmega2560 bootloader | `PROGRAMMER=wiring PORT=<serial port> AVRDUDE_FLAGS="-b 115200 -D"` |
| ATmega32U4 bootloader | `PROGRAMMER=avr109`, 57600, `-D`; the port appears after a 1200-baud touch |
| ATmega4809 over serial UPDI | `avrdude -c serialupdi -p m4809 -P <serial port> -U flash:w:firmware.hex:i`, or `pymcuprog write -d atmega4809 -t uart -u <serial port> -f firmware.hex --erase --verify` |

- avrdude: SerialUPDI needs avrdude 7.0 or later.
- **SerialUPDI wiring:** TX to UPDI through a **1 kOhm** series resistor, RX straight on the UPDI node (pymcuprog); the avrdude manual shows 1 kOhm + diode + 470 Ohm. There is no 4.7 kOhm in either.
- ISP needs a valid target clock; UPDI does not (it runs from its own oscillator).

## Language

C (`-std=gnu11`). C++ only on request, freestanding subset: no STL, no exceptions, no heap. GCC's `__flash` address spaces are a GNU C extension; whether they work in C++ is unverified.
