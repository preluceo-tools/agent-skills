// Deterministic eval gates for the atmega-baremetal skill (docs/skill-scope.md, "Evaluation").
//   node check.mjs examples            compile + grep + lint + headless-sim the skill's own examples and templates
//   node check.mjs project <dir>...    gate one or more project folders the skill wrote (eval outputs)
//   node check.mjs selftest            prove the gates fail on seeded bad projects (evals/fixtures)
// Needs avr-gcc >= 10, avr-libc >= 2.2.0 and make (or mingw32-make) on PATH.
import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdtempSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DiagramLinter } from '@wokwi/diagram-lint';

const here = dirname(fileURLToPath(import.meta.url));
const skill = resolve(here, '../..');

const CLASSIC = ['atmega328p', 'atmega328pb', 'atmega2560', 'atmega1284p', 'atmega32u4', 'atmega168', 'atmega8a', 'atmega8'];
const MEGAAVR0 = ['atmega4809', 'atmega4808', 'atmega3208'];
const SIMULATABLE = ['atmega328p', 'atmega2560'];
const SIM_FILES = ['wokwi.toml', 'diagram.json', 'metadata.json'];

const ARDUINO = /Arduino\.h|\bsetup\s*\(|\bloop\s*\(|digitalWrite|digitalRead|pinMode|analogRead|Serial\.|Wire\.h|SPI\.h/;
// registers that exist only in the other family
const CLASSIC_ONLY = /\bDDR[A-L]\b|\bPIN[A-L]\s*[=&|^]|\bTCCR\d[ABC]\b|\bADMUX\b|\bADCSRA\b|\bUBRR\d?[HL]?\b|\bUCSR\d[ABC]\b|\bSPCR\b|\bTWBR\b|\bTWCR\b|\bMCUSR\b/;
const MEGAAVR0_ONLY = /\bPORT[A-L]\.(DIR|OUT|IN)\w*|\bUSART\d\.|\bTCA0\.|\bTCB\d\.|\bCLKCTRL\.|\bVPORT[A-L]\.|\bSLPCTRL\.|\bRSTCTRL\./;

const makeCmd = ['mingw32-make', 'make'].find((m) => spawnSync(m, ['--version']).status === 0);
const run = (cmd, args, opts = {}) => spawnSync(cmd, args, { encoding: 'utf8', ...opts });
const tail = (r) => (r.stderr + r.stdout).trim().split('\n').slice(-6).join('\n    ');

function walk(dir, ext, out = []) {
  for (const name of readdirSync(dir)) {
    if (name === 'build' || name === 'node_modules') continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p, ext, out);
    else if (ext.some((e) => name.endsWith(e))) out.push(p);
  }
  return out;
}
const stripMakeComments = (s) => s.replace(/^\s*#.*$/gm, '').replace(/\s#.*$/gm, '');
const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\/\/.*$/gm, '');

function makefileVar(dir, name) {
  const f = join(dir, 'Makefile');
  if (!existsSync(f)) return undefined;
  return readFileSync(f, 'utf8').match(new RegExp(`^${name}\\s*[?:]?=\\s*(\\S+)`, 'm'))?.[1];
}

/** Code gates: tokens, family registers, -Wall -Werror compile and link, make hex. Returns failures. */
export function checkCode(dir, mcu, fcpu) {
  const fails = [];
  const srcs = walk(dir, ['.c']);
  const files = walk(dir, ['.c', '.h', '.ino', '.cpp']);
  if (!srcs.length) return [`no .c files in ${dir}`];
  let all = '';
  for (const f of files) {
    const text = stripComments(readFileSync(f, 'utf8'));
    all += text + '\n';
    const a = text.match(ARDUINO);
    if (a) fails.push(`${basename(f)}: Arduino token "${a[0]}"`);
  }
  const mk = join(dir, 'Makefile');
  if (existsSync(mk)) {
    const a = stripMakeComments(readFileSync(mk, 'utf8')).match(/arduino/i);
    if (a) fails.push(`Makefile: Arduino token "${a[0]}"`);
  }
  const wrong = CLASSIC.includes(mcu) ? all.match(MEGAAVR0_ONLY) : all.match(CLASSIC_ONLY);
  if (wrong) fails.push(`wrong-family register "${wrong[0].trim()}" for ${mcu}`);

  const defines = /#\s*define\s+F_CPU\b/.test(all);
  if (!fcpu && !defines) fails.push('F_CPU is not set (Makefile or #define)');
  const tmp = mkdtempSync(join(tmpdir(), 'atm-'));
  const incs = [...new Set(srcs.map((s) => '-I' + dirname(s)))];
  const cc = run('avr-gcc', [`-mmcu=${mcu}`, ...(defines || !fcpu ? [] : [`-DF_CPU=${fcpu}`]), '-std=gnu11', '-Os',
    '-Wall', '-Wextra', '-Werror', ...incs, ...srcs, '-o', join(tmp, 'x.elf')]);
  if (cc.status !== 0) fails.push(`avr-gcc -Wall -Werror failed for ${mcu}:\n    ${tail(cc)}`);

  if (existsSync(mk)) {
    const work = join(tmp, 'proj');
    cpSync(dir, work, { recursive: true, filter: (s) => !/[\\/](build|node_modules)$/.test(s) && !s.endsWith('firmware.hex') });
    const mm = run(makeCmd, ['hex', `MCU=${mcu}`], { cwd: work });
    if (mm.status !== 0 || !existsSync(join(work, 'firmware.hex'))) fails.push(`make hex failed or no top-level firmware.hex:\n    ${tail(mm)}`);
  } else fails.push('no Makefile');
  return fails;
}

/** Project folder gates: code gates for its own MCU plus the simulator project files rule. */
export function checkProject(dir) {
  const mk = join(dir, 'Makefile');
  const mcu = makefileVar(dir, 'MCU');
  if (!mcu) return ['Makefile has no MCU = line'];
  const fails = checkCode(dir, mcu, makefileVar(dir, 'F_CPU'));
  const have = SIM_FILES.filter((f) => existsSync(join(dir, f)));
  if (SIMULATABLE.includes(mcu)) {
    const missing = SIM_FILES.filter((f) => !have.includes(f));
    if (missing.length) fails.push(`simulatable chip ${mcu} lacks ${missing.join(', ')}`);
  } else if (have.length) fails.push(`${mcu} is not simulatable but has ${have.join(', ')}`);
  if (have.includes('diagram.json')) {
    const r = new DiagramLinter().lint(JSON.parse(readFileSync(join(dir, 'diagram.json'), 'utf8')));
    for (const i of r.issues.filter((x) => x.severity === 'error')) fails.push(`diagram.json ${i.rule}: ${i.message}`);
  }
  if (have.includes('wokwi.toml') && !/firmware\s*=\s*'firmware\.hex'/.test(readFileSync(join(dir, 'wokwi.toml'), 'utf8')))
    fails.push("wokwi.toml firmware is not 'firmware.hex'");
  void mk;
  return fails;
}

function report(name, fails) {
  console.log(`${fails.length ? 'FAIL' : 'ok  '} ${name}`);
  for (const f of fails) console.log(`  - ${f}`);
  return fails.length;
}

function stage(example, mcu) {
  const d = mkdtempSync(join(tmpdir(), 'atm-ex-'));
  cpSync(join(skill, 'templates/Makefile'), join(d, 'Makefile'));
  cpSync(example, join(d, 'main.c'));
  return d;
}

function examples() {
  let bad = 0;
  const groups = [['classic', ['atmega328p', 'atmega2560']], ['megaavr0', ['atmega4809', 'atmega4808', 'atmega3208']]];
  let count = 0;
  for (const [fam, mcus] of groups) {
    for (const f of walk(join(skill, 'examples', fam), ['.c'])) {
      count++;
      if (!/SPDX-License-Identifier: (0BSD|MIT)/.test(readFileSync(f, 'utf8'))) bad += report(`${fam}/${basename(f)} licence line`, ['no SPDX 0BSD/MIT line']);
      for (const mcu of mcus) {
        const d = stage(f);
        bad += report(`${fam}/${basename(f)} ${mcu}`, checkCode(d, mcu, makefileVar(d, 'F_CPU')));
      }
    }
  }
  if (count !== 26) bad += report('example count', [`expected 26 examples (18 Tier 1 + 8 Tier 2), found ${count}`]);

  const diagrams = walk(join(skill, 'templates/diagram'), ['.json']);
  const lint = run('node', [join(here, 'lint-diagrams.mjs'), ...diagrams]);
  console.log(lint.stdout.trim());
  bad += lint.status ? 1 : 0;

  // headless avr8js, ATmega328P only: blink period and UART text
  for (const [ex, extra] of [['gpio', ['--ms', '4000', '--blink-ms', '500', '--pin', '5', '--high', '0']], ['usart', ['--ms', '2000', '--text', 'Hello']]]) {
    const d = stage(join(skill, 'examples/classic', ex + '.c'));
    const mm = run(makeCmd, ['hex', 'MCU=atmega328p'], { cwd: d });
    const sim = mm.status === 0 ? run('node', [join(here, 'sim-328p.mjs'), join(d, 'firmware.hex'), ...extra]) : mm;
    bad += report(`avr8js 328P ${ex}`, sim.status ? [tail(sim)] : []);
  }
  return bad;
}

function selftest() {
  let bad = 0;
  const fx = join(here, 'fixtures');
  const expect = { good: null, 'bad-arduino': 'Arduino token', 'bad-family': 'wrong-family', 'bad-vector': 'misspelled', 'bad-no-fcpu': 'F_CPU', 'bad-extra-sim-files': 'not simulatable' };
  for (const [name, want] of Object.entries(expect)) {
    const fails = checkProject(join(fx, name));
    const ok = want === null ? fails.length === 0 : fails.some((f) => f.includes(want));
    console.log(`${ok ? 'ok  ' : 'FAIL'} fixture ${name} ${want ? `must fail with "${want}"` : 'must pass'}`);
    if (!ok) { bad++; fails.forEach((f) => console.log(`  - ${f}`)); }
  }
  return bad;
}

const [mode, ...rest] = process.argv.slice(2);
if (!makeCmd) { console.log('FAIL no make or mingw32-make on PATH'); process.exit(2); }
let bad = 0;
if (mode === 'examples') bad = examples();
else if (mode === 'selftest') bad = selftest();
else if (mode === 'project' && rest.length) for (const d of rest) bad += report(d, checkProject(resolve(d)));
else { console.log('usage: node check.mjs examples | selftest | project <dir>...'); process.exit(2); }
process.exit(bad ? 1 : 0);
