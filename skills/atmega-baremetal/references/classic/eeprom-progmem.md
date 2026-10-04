# Classic AVR: EEPROM and PROGMEM (Tier 2)

Examples: `examples/classic/eeprom.c`, `examples/classic/progmem.c`.

## EEPROM

- `<avr/eeprom.h>`: `eeprom_read_byte/word/block`, `eeprom_update_*`, `eeprom_write_*`, `EEMEM`, `eeprom_busy_wait()`. Prefer `update` (skips the write when unchanged: less wear). Raw registers: `EEARH/L`, `EEDR`, `EECR` (`EEMPE` then `EEPE` within 4 cycles).
- A reset or power loss during a write can corrupt a byte; on older AVRs `EEAR` resets to 0, so an interrupted write can land at address 0. Use the brown-out detector (a fuse setting: `../hazards.md`).
- The Makefile builds `firmware.hex` with `-R .eeprom`, so `EEMEM` initialisers are **not** in it. Treat 0xFF as "never written". To ship initial contents: `avr-objcopy -j .eeprom --change-section-lma .eeprom=0 -O ihex build/firmware.elf eeprom.hex` (standard binutils practice, not checked against simulator loaders).

## PROGMEM

- Classic AVR flash is a separate address space. `const uint8_t t[] PROGMEM = {...}` keeps it in flash; read it with `pgm_read_byte/word/dword(&t[i])` from `<avr/pgmspace.h>`. A plain dereference reads SRAM and returns garbage.
- String literals eat SRAM unless wrapped in `PSTR("...")` and read with the `_P` function variants.
- Above 64 KB (ATmega2560 256 KB, ATmega1284P 128 KB): `RAMPZ` and `ELPM`; `pgm_read_byte_far(addr)`, `pgm_get_far_address(var)`, `PROGMEM_FAR` (avr-libc 2.2+); GCC named address spaces `__flash`, `__flash1`..`__flash5`, `__flashx`, `__memx` (a GNU C extension; whether it works in C++ is unverified). Function pointers beyond 128 KiB need `-mrelax` at link.
