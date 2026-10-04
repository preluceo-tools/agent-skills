# Hazards and Tier 3 topics

Tier 3 = hazard list and datasheet pointer, no code. Name the hazard, say which datasheet chapter to read, and write nothing that touches the setting unless the user asks explicitly and has read the hazard.

## Fuses and lock bits

**Never write fuses by default; never copy a fuse set between chips.** Warn every time a task touches the clock source, the reset pin, debug, or programming.

Fuse-brick hazards, Classic AVR (ATmega328P datasheet unless noted):
- **`CKSEL` set to a source that is absent** (e.g. an external crystal not fitted): no clock, so ISP fails. Recover by supplying a clock on XTAL1, then ISP.
- **`RSTDISBL`**: the RESET pin becomes I/O (PC6 on the 328P); serial ISP needs RESET, so only HVPP can recover. **`SPIEN`** is not accessible in serial programming mode: clearing it needs HVPP.
- **`DWEN`**: RESET becomes the debugWIRE pin; external reset stops working. Clearing it needs a debugWIRE-capable tool; the recovery procedure is **unverified** (not read from a primary source).
- **`JTAGEN`** (2560, 32U4, 1284P): PF4-PF7 (2560) are not usable as GPIO/ADC while enabled. Arduino bootloader fuses disable it. The ATmega2560's factory default is **unverified** (believed programmed; the datasheet table could not be read). Never ship `OCDEN` programmed (it costs power). `MCUCR.JTD` disables JTAG at run time.
- **`CKDIV8`** is programmed on a fresh part: 8 MHz RC becomes 1 MHz. `F_CPU` must match the real clock. The low fuse byte holds `CKDIV8` and the clock source together: any new low-fuse value decides both.
- The Arduino bootloader fuse sets are `boards.txt` values for those boards: Uno `lfuse 0xFF, hfuse 0xDE, efuse 0xFD, lock 0x0F`; Mega 2560 `0xFF/0xD8/0xFD`; Leonardo `0xFF/0xD8/0xCB`. Do not copy them to another device.
- avr-libc fuse macros on Classic AVR are **inverted**: a "programmed" fuse is bit 0, so `1` means unprogrammed. `FUSES = {LFUSE_DEFAULT, ...}` from `<avr/fuse.h>`.

megaAVR 0-series: fuses are written only over UPDI; avr-libc fuse macros are **not inverted** and avr-libc warns "you can damage a device"; a locked device can be unlocked only by CHIPERASE, which erases everything. The 40-pin ATmega4809 needs PB[5:0] and PC[7:6] disabled or pulled up (`megaavr0/chips.md`).

## Programming and recovery

- **PlatformIO** has `pio run -t fuses` and `-t bootloader` targets that write fuses; see `platformio.md`. Plain `-t upload` is the flash write.

- **ISP** programs flash, EEPROM, **fuses and lock bits** (not flash only). The programmer drives SCK/MOSI/MISO and holds RESET low; the application's SPI slaves on those pins see the traffic: keep chip selects inactive or isolate them.
- **High-voltage programming** on the Classic parts is HVPP (parallel), not "HV serial": 11.5-12.5 V on RESET with Vcc at 4.5-5.5 V; on the 328P 18 signal pins are involved. The UPDI 12 V pulse exists on shared-pin tinyAVR parts only, never on the megaAVR 0-series; do not pulse a UPDI pin configured as an output.

## Voltage versus clock (speed grades are linear between points)

ATmega328P/328PB/1284P: 4 MHz at 1.8 V, 10 MHz at 2.7 V, 20 MHz at 4.5 V (16 MHz needs about 3.8 V; 3.3 V allows about 13 MHz, derived). ATmega2560: 16 MHz at 4.5-5.5 V only (2560V 8 MHz at 2.7 V). ATmega32U4: 8 MHz at 2.7 V, 16 MHz at 4.5 V. ATmega8A: 0-16 MHz. ATmega4809: 5 MHz at 1.8 V, 10 MHz at 2.7 V, 20 MHz at 4.5 V up to 105 C; 8 MHz at 2.7 V, 16 MHz at 4.5 V up to 125 C.

## Other Tier 3 topics (datasheet pointer only)

- **Bootloader and SPM:** `<avr/boot.h>`; `BOOTSZ` and `BOOTRST` fuses; SPM runs only from the boot section. 0-series: `BOOTEND`/`APPEND` fuses.
- **Extended flash above 64 KB (2560, 1284P):** `RAMPZ`/`ELPM`, `EIND`; see `classic/eeprom-progmem.md`.
- **ATmega32U4 USB:** device registers (`USBCON`, `UDCON`, endpoints, 832 B DPRAM) and a PLL for 48 MHz. Class stacks such as LUFA are third-party; their licence and status are unverified here.
- **Event System and CCL** (0-series only): `EVSYS` channels and users, `CCL` up to 4 LUTs.
- **Brown-out:** `BODLEVEL` fuses (Classic), `BODCFG` (0-series); `sleep_bod_disable()`.

## Unverified items the skill must not state as fact

ATmega2560 `JTAGEN` factory default; the debugWIRE-to-ISP recovery procedure; the meaning of the 1284P `DWEN` fuse bit; differences between ATmega328P and 328PB beyond the renamed registers (app note AT15007 not read); whether `__flash` works in C++; datasheet revisions newer than those read (328P rev B, 2560 DS40002211A); the ATmega4809 factory `OSCCFG`; the 0-series power-down wake sources; third-party USB stacks.
