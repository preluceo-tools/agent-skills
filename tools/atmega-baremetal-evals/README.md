# atmega-baremetal evals tooling

The scripts that test the `atmega-baremetal` skill. They are not part of the skill: the skill folder
holds only the two eval files, `skills/atmega-baremetal/evals/trigger-evals.json` and
`quality-evals.json`.

| File | What it does |
|---|---|
| `check.mjs` | Deterministic gates, no model: compiles the skill's examples, greps for Arduino calls and wrong-family registers, checks `F_CPU` and the simulator files, lints the diagrams. |
| `sim-328p.mjs` | Headless ATmega328P run in avr8js: LED edge spacing and USART text. |
| `lint-diagrams.mjs` | Lints `diagram.json` files with `@wokwi/diagram-lint`. |
| `fixtures/` | Seeded bad projects that `check.mjs selftest` uses to prove the gates fail when they should. |

## Run the gates

You need avr-gcc 10 or later, avr-libc 2.2.0 or later and GNU make (`mingw32-make` on Windows) on the
`PATH`, plus [Node.js](https://nodejs.org/).

```text
cd tools/atmega-baremetal-evals
npm install
node check.mjs examples        # compile, lint and headless-run the skill's own examples
node check.mjs selftest        # prove the gates fail on seeded bad projects
node check.mjs project <dir>   # gate a project folder the skill wrote
```

## Run the model-graded evals

These use the runners of the grounded-skill-builder skill. They load the skill by name from your
skills folder, so first copy `skills/atmega-baremetal/` to `~/.claude/skills/atmega-baremetal/` (a
copy, not a link), then run, from the repository root:

```text
python <skills folder>/grounded-skill-builder/scripts/run_trigger_evals.py skills/atmega-baremetal --trials 3
python <skills folder>/grounded-skill-builder/scripts/run_quality_evals.py skills/atmega-baremetal --trials 2
```

Add `--pilot` first to see what a run will cost. The runners call the `claude` command-line tool,
which uses your Claude account's usage. Run the gate script on the folders the quality runs write:
`node check.mjs project <run folder>` (delete a seeded input such as `blink.ino` from a copy first).
