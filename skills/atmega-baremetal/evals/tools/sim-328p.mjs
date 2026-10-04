// Headless ATmega328P run in avr8js. Based on the validated simulation research (section 2.1).
// usage: node sim-328p.mjs <firmware.hex> [--hz 16000000] [--ms 2000] [--text Hello] [--blink-ms 500 --pin 5] [--high 0]
// --high <bit>: hold PB<bit> high (a released active-low button). avr8js does not model internal pull-ups:
// an undriven input reads 0 until setPin() is called.
// Exit 1 if the expected serial text is missing or the PB<pin> edge spacing is off by more than 5%.
import { readFileSync } from 'node:fs';
import avr8js from 'avr8js';
import intelhex from 'intel-hex';
const { CPU, AVRTimer, AVRIOPort, AVRUSART, avrInstruction, timer0Config, timer1Config, timer2Config,
        portBConfig, portCConfig, portDConfig, usart0Config } = avr8js;

const args = process.argv.slice(2);
const hexPath = args.shift();
const opt = (name, dflt) => { const i = args.indexOf(`--${name}`); return i < 0 ? dflt : args[i + 1]; };
const hz = +opt('hz', 16000000), ms = +opt('ms', 2000), text = opt('text', ''), blinkMs = +opt('blink-ms', 0), pin = +opt('pin', 5), high = opt('high', '');

const flash = new Uint16Array(0x4000);                      // 32 KB flash
new Uint8Array(flash.buffer).set(intelhex.parse(readFileSync(hexPath)).data);
const cpu = new CPU(flash, 2048);                           // 2 KB SRAM; the library default is 8192
for (const c of [timer0Config, timer1Config, timer2Config]) new AVRTimer(cpu, c);
const portB = new AVRIOPort(cpu, portBConfig);
new AVRIOPort(cpu, portCConfig); new AVRIOPort(cpu, portDConfig);
if (high !== '') portB.setPin(+high, true);
const usart = new AVRUSART(cpu, usart0Config, hz);          // the clock passed here must equal F_CPU

let serial = '';
usart.onByteTransmit = (b) => { serial += String.fromCharCode(b); };
const edges = [];
portB.addListener((v, old) => { if (((v ^ old) >> pin) & 1) edges.push(cpu.cycles / hz * 1e3); });

while (cpu.cycles < hz * ms / 1e3) { avrInstruction(cpu); cpu.tick(); } // tick() after every instruction is mandatory

let ok = true;
if (text && !serial.includes(text)) { console.log(`FAIL serial lacks ${JSON.stringify(text)}; got ${JSON.stringify(serial)}`); ok = false; }
if (blinkMs) {
  const gaps = edges.slice(2).map((t, i) => t - edges[i + 1]);   // skip the first edge: it includes start-up
  const bad = gaps.filter((g) => Math.abs(g - blinkMs) > blinkMs * 0.05);
  if (gaps.length < 2 || bad.length) { console.log(`FAIL PB${pin} edge gaps ${gaps.map((g) => g.toFixed(1))} ms, wanted ${blinkMs} ms`); ok = false; }
}
console.log(ok ? `ok   ${hexPath}: ${edges.length} PB${pin} edges, serial ${JSON.stringify(serial.slice(0, 24))}` : 'FAILED');
process.exit(ok ? 0 : 1);
