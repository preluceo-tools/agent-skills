<div align="center">

# atmega-baremetal

### Write register-level C firmware for ATmega chips: no Arduino framework, a portable Makefile, and simulator files when a simulator can run the chip.

<img src="https://img.shields.io/badge/Claude%20Code-skill-b1b9f9?style=flat-square&labelColor=0d1117" alt="Claude Code skill" />
<img src="https://img.shields.io/badge/Agent%20Skills-spec%20valid-b1b9f9?style=flat-square&labelColor=0d1117" alt="Valid against the Agent Skills specification" />
<img src="https://img.shields.io/badge/examples-compile--checked-b1b9f9?style=flat-square&labelColor=0d1117" alt="26 compile-checked examples" />
<img src="https://img.shields.io/badge/license-0BSD%20%C2%B7%20CC%20BY%204.0-b1b9f9?style=flat-square&labelColor=0d1117" alt="0BSD and CC BY 4.0" />

</div>

This is an agent skill for Claude Code. It writes bare-metal C firmware for ATmega microcontrollers
with avr-gcc and avr-libc, using the register names from the datasheet. It also writes the Makefile
that builds and flashes it. For the two chips a simulator can run, it writes the Wokwi project files
as well.

> [!NOTE]
> **Unofficial.** This project is not affiliated with, endorsed by, or supported by Anthropic,
> Microchip, Arduino or Wokwi. Claude Code, Microchip, Arduino and Wokwi are named here only to say
> which tools and parts the skill works with.

> [!IMPORTANT]
> **Not yet tested on real projects, and the evals are small.**
>
> - **Reduced evals.** The model-graded evaluations were run at reduced size to limit usage cost: 3 trials per
>   trigger prompt, and 1 to 3 trials per quality scenario (2 for most; the ATmega4809 comparison without the
>   skill has 2, and the fuse-hazard scenario had a single follow-up trial). Pass rates are therefore rough
>   indications, not statistically strong results, and the scope of the runs is limited. One fuse-hazard trial
>   missed a criterion (it matched an Arduino board's fuse set without saying not to copy it); more trials are
>   needed to know whether that is noise.
> - **No real-world testing yet.** The skill has not been used to build a project on real hardware. The evals
>   may look clean, but the skill needs proper testing by building a project for AVR hardware, on each AVR
>   microcontroller it supports, before you rely on it. Treat its output as a draft to compile, flash and
>   verify yourself.

---

## Contents

- [What it does](#what-it-does)
- [Install](#install) · [Use](#use)
- [Which chips](#which-chips)
- [Does it work? Measured evals](#does-it-work-measured-evals)
- [Other skills it works with](#other-skills-it-works-with)
- [Files](#files)
- [Built with](#built-with)
- [Credits](#credits)
- [Disclaimer](#disclaimer) · [License](#license)

---

## What it does

- **Names the family first.** Before any register code, the agent states whether your chip is a
  *Classic AVR* (`DDRx`/`PORTx`/`PINx` registers, ISP programming, e.g. ATmega328P) or a *megaAVR
  0-series* (`PORTx.DIR`, `USARTn.BAUD`, UPDI programming, e.g. ATmega4809). The two register models
  share almost nothing, and code for one does not build for the other.
- **Writes a flat project folder:** `main.c`, a `Makefile`, `firmware.hex` at the top level, and
  `build/` for the objects and the ELF. The Makefile has `build`, `size`, `hex`, `flash` and `clean`
  targets and never writes fuses or lock bits.
- **Works in a PlatformIO project.** If there is a `platformio.ini`, it writes a no-framework
  project (`src/main.c`, no `framework` line, no Makefile) and points `wokwi.toml` at the
  `.pio/build/<env>/` output. It will not suggest `pio run -t fuses` or `-t bootloader` unprompted.
- **Covers the common peripherals** with a recipe per family and a compile-checked example: GPIO,
  clock and `F_CPU`, timers and PWM, USART, ADC, external and pin-change interrupts, ISR and atomic
  rules, sleep and power, watchdog, and (shorter) SPI, TWI, EEPROM and PROGMEM.
- **Warns instead of coding** for fuses, lock bits, bootloaders, flash above 64 KB, USB, the Event
  System and on-chip debug: it lists the hazards and points you at the datasheet.
- **Ports an existing Arduino sketch** to bare metal. It does not write new Arduino sketches.
- **Writes simulator files only where a simulator exists:** `wokwi.toml`, `diagram.json` and
  `metadata.json` for the ATmega328P and ATmega2560. For every other chip it says plainly that no
  supported simulator exists.
- **Says what it did not check.** Facts the research could not confirm are written as *unverified*,
  never as facts, and the agent says whether the code was compiled.

---

## Install

Copy the `atmega-baremetal` folder into your personal skills folder:

```text
~/.claude/skills/atmega-baremetal/
```

On Windows that is `%USERPROFILE%\.claude\skills\atmega-baremetal\`. To limit the skill to one
project, put it in `<project>/.claude/skills/atmega-baremetal/` instead.

The firmware needs tools on the machine that builds it. None of them ships with the skill:

- **avr-gcc 10 or later with avr-libc 2.2.0 or later.** Older toolchains work for Classic chips; the
  megaAVR 0-series needs these versions.
- **GNU make.** On Windows it may be called `mingw32-make`.
- **avrdude**, for `make flash`.

## Use

Name the chip and say what you want, for example:

- "Write bare-metal C for an ATmega328P that blinks an LED on PB5 every 500 ms, with a Makefile I can
  flash with a usbasp."
- "Set up USART0 at 115200 baud on an ATmega4809, no framework."
- "Port this Arduino sketch to bare-metal AVR C for the Uno."

Build in the project folder, then flash:

```text
make MCU=atmega328p F_CPU=16000000UL
make flash PORT=<serial port>
```

ISP programmers such as a usbasp need no `PORT`. `F_CPU` must equal the real clock of your chip: a
fresh Classic part runs at 1 MHz because its `CKDIV8` fuse is programmed, not at 8 MHz.

> [!WARNING]
> **Check the pins.** The examples use example pins (an LED on `PB5`, or `PF5` on the 0-series). They
> were compiled, not run on hardware. Confirm every pin against your board before you flash.

---

## Which chips

| Support | Chips | What you get |
|---|---|---|
| First-class | ATmega328P, ATmega2560, ATmega4809 (also covers 4808 and 3208) | Full recipes and compiled examples |
| Differences table | ATmega328PB, 1284P, 32U4, 168 | The first-class recipe plus how the chip differs |
| Warn only | ATmega8A | The agent says it does not write full code and lists the traps |
| Simulatable | ATmega328P, ATmega2560 | `wokwi.toml`, `diagram.json`, `metadata.json` |

Other chips (ATtiny, XMEGA, AVR Dx, ARM, ESP32) are outside the skill. The ATmega4809 cannot be
simulated: Wokwi lists it as "not planned" and no other simulator covers it.

### Running the simulator files in another viewer: a guess, not tested

The skill writes `metadata.json` because it is the project file read by the
[avr8js Electron Playground](https://github.com/arcostasi/avr8js-electron-playground), a desktop simulator. **That is an assumption, and nothing here
has been run in it.** What follows comes from reading the playground's source, not from using it:

- It appears to list a folder as a project when it holds `metadata.json` (or at least `diagram.json`),
  and to take the board from the `diagram.json` board part (`wokwi-arduino-uno`, `-nano`, `-mega`).
- It appears to convert Wokwi's tuple-format `diagram.json` to its own format on load, and to load a
  `.hex` file from the project folder as the firmware, so the `firmware.hex` the Makefile writes
  at the top level should run without compiling. Run `make` first: it loads whatever hex is there.
- It does not read `wokwi.toml`.
- Do not use its Build / Compile button. It builds Arduino sketches (in the cloud or with
  `arduino-cli`), not a bare-metal `main.c`.
- It marks the ATmega2560 as partially supported, and saving from it writes a diagram that Wokwi
  cannot open.
- Its repository has no `LICENSE` file; its `package.json` says MIT.

Treat all of this as unconfirmed until someone opens a generated project in it. Wokwi remains the
documented way to run the files.

---

## Does it work? Measured evals

The figures below come from running the two eval files in `evals/` with Claude Sonnet 5.5 in Claude
Code, plus the deterministic gates in
[`evals/tools/`](evals/tools/). Runs that ended at a permission
prompt or with an unreadable grade say nothing about the skill. Such runs were discarded, and none is counted below.

> [!WARNING]
> **The evals cost usage.** Each run calls the `claude` command-line tool, once per prompt, per trial
> and per condition, and once more for each grade. A full pass is 39 trigger runs and 28 quality runs, and the
> quality runs alone used a large share of a five-hour usage window.

### Trigger evals: does the skill start when it should?

| | Runs | Correct |
|---|---|---|
| Should start (7 prompts) | 21 | **21** |
| Should stay quiet (6 prompts) | 18 | **18** |

The quiet prompts were a new Arduino sketch, STM32 bare-metal code, Arduino IDE help, ESP32 firmware,
an ATtiny85 project and a PlatformIO ESP32 library error. These show only that the skill starts. A skill that is not loaded cannot
start, so trigger evals cannot compare with and without.

The two PlatformIO start prompts and the PlatformIO quiet prompt were added after the other ten, with
the description lengthened to mention PlatformIO. They were run on their own (3 runs each, 9 of 9
correct); the other ten were not re-run after the description changed.

### Quality evals: is the result better with the skill?

Seven scenarios, 2 runs per scenario and condition (3 with-skill runs for the fuse scenario). A
separate grader, which did not know the condition, scored each run against a rubric of 7 to 10 points.

| Scenario | With skill | Without skill |
|---|---|---|
| ATmega328P blinker with serial output, simulatable | 20/20 | 8/20 |
| ATmega4809 blinker with serial output, no simulator | 20/20 | 15/20 (see limits) |
| Port an Arduino sketch to the Uno | 19/20 | 12/20 |
| Move an ATmega328P to an external crystal (fuse hazards) | 28/30 | 14/20 |
| ATmega32U4 serial output (differences table) | 18/18 | 12/18 |
| ATmega8A blinker (warn-only chip) | 14/14 | 7/14 |
| PlatformIO project for an Uno, Arduino framework removed | 18/18 | 14/18 |
| **All seven** | **137/140 (98 %)** | **82/130 (63 %)** |

The with-skill and without-skill totals do not cover the same number of runs (the fuse scenario had
three with-skill runs and two without), so compare the percentages, not the counts. In the
PlatformIO scenario the baseline missed only the family gate and the statement that PlatformIO
supplies `F_CPU`. Its fuse criteria pass either way, because nothing in the prompt tempts a fuse
write, so that scenario does not test the fuse warning.

What changed in the output, counted over the runs whose rubric asked for it:

| Observation | With skill | Without skill |
|---|---|---|
| Started with the family gate | 13 of 13 runs | 0 of 12 |
| Wrote the simulator files for a simulatable chip | 4 of 4 | 0 of 4 |
| Makefile with a `hex` rule that writes `firmware.hex` at the top level | 6 of 6 | 0 of 6 |
| Said plainly that the ATmega32U4 cannot be simulated | 2 of 2 | 0 of 2 |
| Warned about the high-voltage-recovery fuse bits (`RSTDISBL`, `SPIEN`, `DWEN`) | 3 of 3 | 0 of 2 |
| Said the ATmega8A is warn-only and listed its traps | 2 of 2 | 0 of 2 |
| Used `UBRR1` on the 32U4 (it has no `UBRR0`) | 2 of 2 | 2 of 2 |
| Warned that a crystal clock with no crystal fitted stops ISP | 3 of 3 | 2 of 2 |
| Did not define `F_CPU` in the PlatformIO source, or said PlatformIO supplies it | 2 of 2 | 0 of 2 |

Where the baseline did as well, it is listed: a capable model already knows the 32U4 has one USART
and that a missing crystal kills the clock. The skill's gain is the project shape, the family gate,
the simulator files and the warnings a default answer leaves out.

### Deterministic gates: does the code compile and look right?

These run without a model:

| Gate | Result |
|---|---|
| 26 examples (13 Classic, 13 megaAVR 0-series) compile with `-Wall -Wextra -Werror` for ATmega328P and 2560 (Classic) and ATmega4809, 4808 and 3208 (0-series) | 65 of 65 builds pass |
| The three board diagrams pass `@wokwi/diagram-lint` | 3 of 3 |
| avr8js, ATmega328P only: LED edge spacing within 5 % of 500 ms, and the text `Hello` on USART0 | both pass |
| Seeded bad projects (an Arduino sketch, wrong-family registers, a misspelled vector, no `F_CPU`, simulator files for a chip with no simulator) | 5 of 5 fail as they should, 1 good project passes |
| Projects the skill wrote in the quality runs (compile, no Arduino calls, right-family registers, `F_CPU` set, simulator files only for a simulatable chip) | 10 of 10 pass |

The gate caught a defect the grader did not: one 4809 run `#define`d `BAUD`, which collides with the
`USART0.BAUD` register member and does not compile. The skill now says never to do that.

### Known limits

- **Not a held-out test.** The scenarios were re-run after each fix, and the fixes were made while
  looking at those same scenarios. The figures are the last runs of each scenario. They show the skill
  does what its instructions say, not how it does on prompts nobody looked at.
- **Remaining weaknesses.** In the fuse scenario, 1 of 3 runs did not say that a fuse set copied from
  an Arduino board definition must not be copied, nor that `F_CPU` must equal the real clock; the
  other two runs passed every criterion. In the Arduino port, 1 of the 2 counted runs did not name
  the timer behind the `millis()` replacement; 3 further runs made after that (not in the table, and
  their run folders were not kept) named it every time.
- **Rubric edits.** After the first run, the "no Arduino token" criteria were changed to exempt
  comments, the seeded sketch, a self-written `millis()` and the `wokwi-arduino-*` part names. Those
  had failed runs that met the intent. The ATmega8A baseline runs were graded before that edit.
- **The ATmega4809 baseline comes from a re-run.** The first two baseline runs stopped at a permission
  prompt (the model tried a web search) and were discarded. After web tools were blocked in the
  runner, two valid baseline runs scored 8/10 and 7/10 (the table's 15/20). Those run folders were
  not kept, so the figure rests on the recorded scores. The baseline missed the family gate, the
  statement that no simulator runs the 4809, and once the `OSCCFG` note.
- **The family-gate row measures the skill's own convention.** A baseline has no reason to state a
  gate; the row shows the behaviour is present, not that the baseline was wrong.
- **Compiled, not run.** Only the ATmega328P was simulated, headlessly. Nothing ran on hardware.
- **PlatformIO is checked for Classic AVR only.** A bare-metal ATmega328P (`atmelavr`) project was
  built with PlatformIO Core; a bare-metal ATmega4809 build on the `atmelmegaavr` platform was not
  tried, and the skill says so. The fuse targets come from the PlatformIO documentation and were not
  run.

> [!NOTE]
> **How far these numbers go.** They cover one skill, one model, seven scenarios and 2 or 3 runs per
> scenario and condition. They show a clear, consistent difference, not a precise size. The baseline
> switches off **all** skills, not only the one under test. The grader is a Claude model too. It
> sees only the files and the final message, never the condition.

---

## Other skills it works with

**atmega-baremetal calls no other skill.** It is complete on its own.

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The instructions the agent follows: hard rules, workflow, a router to the references, gotchas. |
| `references/classic/*.md` | Classic AVR: chips and nine topic files, read only after the family gate. |
| `references/megaavr0/*.md` | The same topics for the megaAVR 0-series. |
| `references/toolchain.md` | Toolchain floor, the Makefile, flashing over ISP and UPDI. |
| `references/platformio.md` | Building with PlatformIO: the bare-metal `platformio.ini`, `F_CPU`, the fuse targets to avoid. |
| `references/simulation.md` | Which chips can be simulated, the simulator files, pitfalls. |
| `references/hazards.md` | Fuses, programming, voltage against clock, and the topics that get a warning instead of code. |
| `templates/` | The Makefile, `wokwi.toml`, and `diagram.json` and `metadata.json` per board. |
| `examples/classic/`, `examples/megaavr0/` | 13 compile-checked C files per family. |
| `evals/trigger-evals.json` | Test prompts: seven that should start the skill and six that should not. |
| `evals/quality-evals.json` | Test scenarios, each with seeded files and a rubric, run with and without the skill. |
| `evals/tools/` | Node.js gates, a headless ATmega328P run and seeded bad projects for testing the skill (not in the zip). |
| `LICENSE`, `LICENSE-docs` | The license texts, see [License](#license). |

The deterministic gate script, the headless ATmega328P run and the seeded bad projects are in
[`evals/tools/`](evals/tools/). They are for testing the skill, not part of it: the agent never reads
them, and the distribution zip leaves them out. They need Node.js.

---

## Built with

**Nothing has to be downloaded to install the skill.** The firmware it writes needs the free tools
marked *toolchain*. Only Claude Code is commercial.

| Component | What the tool uses it for | Where it comes from | License |
|---|---|---|---|
| [Claude Code](https://www.anthropic.com/claude-code) | Runs the skill: reads the instructions, writes the project | Anthropic; needs a Claude subscription or API account | **Commercial** |
| avr-gcc and binutils (toolchain) | Compile, link, `avr-objcopy`, `avr-size` | [GCC](https://gcc.gnu.org/), [GNU Binutils](https://sourceware.org/binutils/); packaged by distributions or as a Windows build | GPL v3 or later |
| avr-libc (toolchain) | C library, device headers, `<avr/*.h>`, `<util/*.h>` | [avr-libc](https://github.com/avrdudes/avr-libc) | Modified BSD |
| GNU make (toolchain) | Runs `templates/Makefile`; `mingw32-make` on Windows | [GNU make](https://www.gnu.org/software/make/) | GPL v3 or later |
| avrdude (toolchain, for `make flash`) | Programs flash over ISP, UPDI, JTAG and bootloaders | [avrdude](https://github.com/avrdudes/avrdude) | GPL v2 or later |
| Optional: pymcuprog | Alternative UPDI programmer for the ATmega4809 | [pymcuprog on PyPI](https://pypi.org/project/pymcuprog/) | MIT |
| Optional: PlatformIO Core | Builds and uploads the project when the user works in PlatformIO (e.g. in VS Code) | [PlatformIO](https://platformio.org/), [source](https://github.com/platformio/platformio-core) | Apache-2.0 |
| Optional: Microchip ATmega_DFP | Device headers and specs for the megaAVR 0-series on an older GCC | [Microchip packs](https://packs.download.microchip.com/) | Apache-2.0 |
| Optional, untested: [avr8js Electron Playground](https://github.com/arcostasi/avr8js-electron-playground) | A possible desktop viewer for the generated `diagram.json`, `metadata.json` and `firmware.hex` (see above; not run) | [GitHub repository](https://github.com/arcostasi/avr8js-electron-playground) | MIT per its `package.json`; the repository has no `LICENSE` file |
| Optional: Wokwi | Simulates the ATmega328P and ATmega2560 from `diagram.json` and `wokwi.toml` | [Wokwi](https://wokwi.com/); its VS Code extension, command-line tool and web editor have their own terms (free for personal and open-source use, paid tiers above that) | Proprietary service; [avr8js](https://github.com/wokwi/avr8js) and [wokwi-cli](https://github.com/wokwi/wokwi-cli) are MIT |

The evals add dev dependencies that are not part of the skill: [Node.js](https://nodejs.org/) (MIT),
[avr8js](https://github.com/wokwi/avr8js) (MIT), [intel-hex](https://github.com/bminer/intel-hex.js)
(MIT) and [@wokwi/diagram-lint](https://github.com/wokwi/wokwi-cli) (MIT in its LICENSE file; its
package metadata says ISC), plus the grounded-skill-builder skill that runs them.

The skill ships no third-party code. The device facts come from the vendors' datasheets and the
avr-libc and avrdude manuals; the examples and the Makefile are original.

---

## Credits

- The skill was built, and its quality evals were run, with the **grounded-skill-builder** skill.
- Its scope was worked out with the `grill-with-docs` skill from
  **[Matt Pocock's skills](https://github.com/mattpocock/skills)** (MIT).
- The device facts were validated against Microchip's datasheets and application notes, the avr-libc
  and avrdude manuals, and the Wokwi documentation and source.

---

## Disclaimer

This skill is provided **"as is", without warranty of any kind**, express or implied, including but
not limited to the warranties of merchantability, fitness for a particular purpose and
non-infringement. You use it entirely at your own risk.

The author and contributors are not liable for any claim, damage or other loss arising from its use
or from being unable to use it. That includes a chip left without a clock or a reset pin by a fuse
change, firmware that does not behave as written, and anything done with the code or the commands the
agent gives you. Checking pins, voltages, clocks and fuse values against your datasheet is your
responsibility.

The licenses below say the same in their own terms (0BSD; CC BY 4.0, section 5). Where this summary
and a license differ, the license applies.

## License

© 2026 preluceo

**The code**, meaning `examples/` and `templates/`, is licensed under the
[BSD Zero Clause License](https://opensource.org/license/0bsd) (see [`LICENSE`](LICENSE)). It is
permissive on purpose: firmware you generate from it carries no obligation.

**The prose**, meaning `SKILL.md`, the reference files and this manual, is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see [`LICENSE-docs`](LICENSE-docs)). You
may share and adapt it for any purpose if you give credit.

*This summary is not a license. The linked texts are the actual terms.*
