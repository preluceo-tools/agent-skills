# megaAVR 0-series chips

Family: struct-style registers (`PORTx.DIR`, `USARTn.BAUD`), CCP-protected registers, UPDI programming. AVRxt core: `sbi` takes 1 cycle. **None of the Classic names exist**: no `DDRx`, `TCCR1A`, `ADMUX`, `UBRR0`, no `PRR`, no `<util/setbaud.h>` use, no `power_*` macros.

## First-class chip: ATmega4809 (covers 4808 and 3208)

| Chip | Flash | SRAM | EEPROM |
|---|---|---|---|
| ATmega4809 | 48 KB | 6 KB | 256 B |
| ATmega4808 | 48 KB | not read | not read |
| ATmega3208 | 32 KB | not read | not read |

- Clock: 20 MHz only at 4.5-5.5 V up to 105 C; the 125 C grade is 16 MHz. 10 MHz at 2.7 V, 5 MHz at 1.8 V (105 C grade).
- **Reset state: `CLK_PER = CLK_MAIN / 6`** (`MCLKCTRLB = 0x11`). Main-clock sources are OSC20M, OSCULP32K, XOSC32K (32.768 kHz crystal) and EXTCLK: no crystal oscillator above 32.768 kHz. OSC20M runs at 16 or 20 MHz according to the `OSCCFG` fuse; the Arduino Nano Every / Uno WiFi Rev2 board definitions set 16 MHz. The factory `OSCCFG` value is not in the validated research: read the fuse before choosing `F_CPU`.
- Peripherals: `PORTx`/`VPORTx`, TCA0 (16-bit), TCB0-3, RTC, WDT, `USART0..3`, `SPI0`, `TWI0`, `ADC0`, `EVSYS`, `CCL` (Tier 3). No ICP pin; capture runs through the Event System.
- Programming and debug: **UPDI**, a dedicated pin; RESET is a separate pin (PF6) with the `RSTPINCFG` fuse. No fuse disables the UPDI pin, and 12 V activation does not apply (that exists on shared-pin tinyAVR only). Boards: Arduino Nano Every, Uno WiFi Rev2, ATmega4809 Curiosity Nano. No ATmega4808 Curiosity Nano was found.
- **Not simulatable.** Wokwi closed the request "Not planned"; simavr's request is open; Proteus and SimulIDE do not list it.
- The 40-pin ATmega4809 uses the 48-pin die. Pins PB[5:0] and PC[7:6] have no bond pads: set them `INPUT_DISABLE` or pull-up (`PORTx.PINnCTRL`), or they float and draw current.
