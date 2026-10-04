# megaAVR 0-series: EEPROM and flash data (Tier 2)

Examples: `examples/megaavr0/eeprom.c`, `examples/megaavr0/progmem.c`.

## EEPROM

- Memory-mapped at 0x1400 and written through `NVMCTRL` commands with a page buffer. `<avr/eeprom.h>` (`eeprom_read_byte`, `eeprom_update_byte`, `EEMEM`) compiles and links for the 4809 and hides it; `eeprom_update_*` still saves wear.
- The Makefile strips `.eeprom` from `firmware.hex` (`-R .eeprom`): an `EEMEM` initialiser is not programmed. Treat 0xFF as "never written".
- The fuse and USERROW areas are reachable over UPDI only.

## Flash data

Flash is mapped into data space from 0x4000 (`__RODATA_PM_OFFSET__` is set for the 4809 by the device specs). A plain `const` array stays in flash and plain loads work, so `PROGMEM` is optional; `PROGMEM` with `pgm_read_*` still works and keeps code portable to Classic AVR. `<avr/flash.h>` (avr-libc 2.3+) adds `__flash`/`__flashx` helpers; the 48 KB part needs no far access.
