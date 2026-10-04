// Lint every diagram.json given on the command line with @wokwi/diagram-lint. Exit 1 on any error.
import { readFileSync } from 'node:fs';
import { DiagramLinter } from '@wokwi/diagram-lint';

let bad = 0;
for (const file of process.argv.slice(2)) {
  const result = new DiagramLinter().lint(JSON.parse(readFileSync(file, 'utf8')));
  const errors = result.issues.filter((i) => i.severity === 'error');
  console.log(`${errors.length ? 'FAIL' : 'ok  '} ${file} (${result.issues.length} issues)`);
  for (const i of result.issues) console.log(`  [${i.severity}] ${i.rule}: ${i.message}`);
  bad += errors.length;
}
process.exit(bad ? 1 : 0);
