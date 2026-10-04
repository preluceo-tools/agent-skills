---
name: grounded-skill-builder
description: Builds a new agent skill (SKILL.md, references, scripts, trigger and quality evals it runs with and without the skill, optional distribution zip) grounded in source material the user supplies, so the skill carries their real expertise instead of generic advice the model already knows. Source material means a transcript of doing the task, a runbook, a corrected agent trajectory, PR review feedback. Also audits an existing skill folder, the user's own or a downloaded one (spec, security scan, README rules, evals with and without the skill), then fixes with consent. Use whenever the user wants to create, draft, or package something as a skill, or asks for a SKILL.md — even a bare "make this a skill" — and whenever they ask to audit or check an existing skill, run its evals, or whether a downloaded skill is safe to install. Demands the source material before writing a new skill. Not for CLAUDE.md / AGENTS.md files, reviewing ordinary code, or scanning package dependencies for vulnerabilities.
license: GPL-3.0 (scripts), CC-BY-4.0 (prose); see LICENSE and LICENSE-docs
metadata:
  version: "1.1.1"
---

# Grounded Skill Builder

A skill is procedural knowledge the model cannot reach on its own. Every line of a skill you build traces back to **source material** the user supplied. The rules behind each step, with citations, live in [references/grounding-rules.md](references/grounding-rules.md) — read it before step 2.

**Audit.** When the user points at an existing skill folder, or a folder of several skills — to audit or check it, run its evals, or ask whether it is safe — this is an Audit, not a Build: *read* [references/audit.md](references/audit.md) and follow it. It reuses the steps below by number.

## 1. Gate on source material

Ask for source material first: a transcript or notes from doing the task by hand, a runbook, a corrected agent trajectory, review or PR comments, past reports. A topic name, a wish list, or "you know how this works" is a request, not source material — reply with what would count and wait.

Session transcripts count: Claude Code keeps them in `~/.claude/projects/<project folder>/*.jsonl`. *Run* `scripts/extract_user_turns.py <files> --grep <word>` to get only what the user typed, which is where the corrections are.

Done when: you hold at least one concrete artifact and have read all of it.

## 2. Mine the source

Extract, citing where in the source each came from:

- **Job** — the one task the skill does, in the user's words.
- **Triggers** — phrasings a user would actually type; and **near-misses** — tasks sharing vocabulary where the skill must stay silent.
- **Gotchas** — every correction in the source is one: an environment fact that defies a reasonable assumption.
- **Fragile steps** — steps that must come out identical every run (arithmetic, exact formats, ordered commands). Each is a script candidate; if nearly every step is fragile, tell the user a plain script may serve better than a skill.
- **Kind** — *capability* (teaches what the model can't yet do; retire when it can) or *preference* (the team's way; durable).
- **Conflicts** — where the source shows one practice and the user's spec or request says another, list each side by side for the user to decide.

Done when: every correction in the source is either a gotcha or struck as something the model already does by default, and every conflict has the user's decision.

## 3. Ask where it installs

Ask every time — project `<repo>/.claude/skills/<name>/` or user `~/.claude/skills/<name>/`. Offer the kind as input: a preference skill tied to one repo's conventions leans project; a capability skill leans user. The user decides.

## 4. Draft the skill

```
<name>/
  SKILL.md
  README.md              written in step 9
  references/            only when a file goes in it
  scripts/               only when a fragile step goes in it
  assets/                only when a template or other file the skill copies goes in it
  evals/trigger-evals.json
  evals/quality-evals.json
```

- **Description** — what it does, when to use it, and the near-misses it excludes; lean pushy, models under-trigger. Name ≤ 64 characters, description ≤ 1024.
- **Body** — skeletal from the first draft: steps, completion criteria, gotchas. Material only some branches need goes straight to `references/`, behind a pointer that says when to read it.
- **Fragile steps** — write them as scripts. The body says *run* `scripts/<x>` or *read* `references/<y>.md`, explicitly, per file.
- **Scripts section** — if `scripts/` exists, the body lists one line per script naming what it touches: filesystem paths, network hosts, credentials or environment variables — or `none`.
- **Smoke check** — every script and asset gets one runnable check before step 5, e.g. render a page template headless and assert its output. Run it; a template the skill fills is where a skill breaks silently.

## 5. Draft the evals

- `evals/trigger-evals.json`: 5 cases with `should_trigger: true` built from the triggers, 5 with `false` built from the near-misses.
- `evals/quality-evals.json`: about 5 scenarios, one per branch of the skill. Each seeds the files the task needs, written out in full: every file or folder the prompt names goes in `files` with its contents, never an empty `files`. Each gives a prompt a user would type, and lists 6–10 rubric criteria a grader can check from the output. When the skill waits for the user (a confirmation, a question), end the prompt with the answer, e.g. "Don't ask me anything first: I accept your draft."

Formats in [references/grounding-rules.md](references/grounding-rules.md#trigger-eval-format). Show both files to the user and apply their edits.

Done when: the user has approved both files.

## 6. Run writing-for-agents

Invoke `mattpocock-skills:writing-for-agents` with the Skill tool now, by name, and apply it to `SKILL.md` and every `references/` file. If that skill isn't installed, say so and move on.

## 7. Strip no-ops in a fresh subagent

Dispatch a fresh subagent (Agent tool, `general-purpose`) given only the skill folder path and this brief: *"List every sentence in these files that would not change a capable model's behavior versus its default — a no-op. Quote each and say why."*

Done when: every flagged sentence is deleted whole, or kept with the behavior it changes stated to the user.

## 8. Run the evals

Run them now, on the final text: every edit in steps 6–7 can change what triggers and what the skill does. Write the folder to the chosen location first, since the runners call the installed skill.

**Security scan — before the evals, which run the skill's scripts:**

1. *Run* `scripts/security_scan.py <skill folder>`. It prints JSON Findings, each `blocking`, `fix` or `note`.
2. Dispatch a fresh subagent (Agent tool, `general-purpose`) given only the skill folder path and this brief: *"Read-only: do not run, edit or create anything. For each file in `scripts/`, list every filesystem path, network host, credential and environment variable it reaches, and compare it with what the Scripts section of SKILL.md declares for that script. Report each undeclared reach as file:line."* Each undeclared reach is a `blocking` Finding.
3. Any `blocking` Finding stops the step: show it to the user and fix it before any eval runs. Fix or justify each `fix`; check each `note` against the Scripts section.
4. When the JSON has `"evals_hold": true`, the scanner could not run: show the user its `command`, `error` and `detail` (cause and fix), and run no eval until the user says go ahead. On a certificate error the fix is `--native-tls`.

Report the scan as best-effort whatever it found: a clean result is not proof the skill is safe.

**Eval cost warning — before every eval run, re-runs included:** *run* the runner first with `--pilot --out <run folder>` and the flags of the planned run. It runs a small slice and prints the run count, the notional USD, the five-hour window now and after, and its reset in local time. Show that to the user and wait for their go-ahead. When the pilot cannot run yet, tell the user those four items are what the warning will show. Above 90%, offer fewer trials, an `--only` subset, or waiting until the reset. Then run the plan with the same `--out`: it reuses the pilot's runs, and every run ends with what it actually spent.

1. *Run* `scripts/run_trigger_evals.py <skill folder> --trials 3`.
2. *Run* `scripts/run_quality_evals.py <skill folder> --trials 2`. It runs each scenario with the skill and without it, and grades every run blind.
3. Read each failed criterion in its run folder (`_transcript.jsonl`, `_grade.json`, the files written) and decide: a skill defect, fixed in the skill, or grader noise, stated to the user.
4. After each fix, re-run the affected scenarios with `--only <ids> --conds skill`.

Runs marked `?` ended in an API error such as a usage limit; re-run them, never count them.

5. Validate against the [Agent Skills specification](https://agentskills.io/specification): *run* `skills-ref validate <skill folder>` with the folder path spelled out: given `.` it reads the folder name as empty and fails. If `skills-ref` is not installed, *run* `uvx --from "git+https://github.com/agentskills/agentskills#subdirectory=skills-ref" skills-ref validate <skill folder>`; on `invalid peer certificate: UnknownIssuer`, add `--native-tls` after `uvx`. Without `uv`, say so and check by hand: `name` matches the folder, lowercase letters, digits and single hyphens, ≤ 64 characters; description ≤ 1024; body under 500 lines. Fix every error and re-run.

Done when: the security scan has no open `blocking` Finding, every trigger case matches in every trial, every failed criterion with the skill is fixed and re-run or explained to the user, and the validator prints `Valid skill`.

## 9. Write the README

Write `README.md` in the skill folder for every skill, shared or not, following the user's rules for distributed tools:

- What it does, install, use, and files.
- An "Agent Skills standard" section: the skill follows the [Agent Skills specification](https://agentskills.io/specification) and passes its validator, `skills-ref validate <skills folder>/<name>`. Name any requirement beyond the spec, e.g. scripts that need Claude Code. Write it only if the validator printed `Valid skill` in step 8.
- A "Built with" table and a License section, always.
- An "Other skills it calls" table when the skill invokes a skill it does not bundle: the skill, the step, where it comes from, its license. Credit its author.

Then ask whether the skill will be shared beyond this machine. If yes, *run* `scripts/make_dist.py <skill folder> <repo>/dist --version <x.y.z>`. It refuses to zip while any file names a path or the user of this machine.

## 10. Hand over

Report the tree, the gotcha count, the security scan's Findings (a clean scan is best-effort), the trigger results, the quality scores with and without the skill, and the validator result.

## Scripts

- `scripts/extract_user_turns.py` reads the transcript files it is given; nothing else.
- `scripts/run_trigger_evals.py` and `scripts/run_quality_evals.py` write run folders under a new temp folder (or `--out`) and call the `claude` CLI, which uses the user's Claude account and usage. Each run blocks shell tools; quality runs may edit files inside their own run folder.
- `scripts/make_dist.py` reads the skill folder and writes one zip into the dist folder; with `--check` it only reads.
- `scripts/evalkit.py` is shared code for the two runners. With `--pilot`, it makes one extra minimal `claude` call to read the five-hour window.
- `scripts/security_scan.py` reads the skill folder, or every skill in a folder of skills; `uvx` downloads the Cisco skill-scanner from github.com and pypi.org on first use, and the scanner runs its static analyzers only, with no API key.
- `scripts/test_scripts.py` checks the shared code on recorded output and runs `scripts/security_scan.py` on seeded folders in a temp folder it deletes; no `claude` calls.
- The step 8 validator, `skills-ref`, is not bundled: it is either installed, or `uvx` downloads it from github.com and pypi.org. It only reads the skill folder.

## Gotchas

- Third-party source material (a video, an article, someone else's talk) is distilled into rules in your own words and cited by URL. The raw text stays out of the skill folder.
- Nothing from this machine goes into the skill: write `<repo>`, `~`, or an environment variable where a path is needed.
