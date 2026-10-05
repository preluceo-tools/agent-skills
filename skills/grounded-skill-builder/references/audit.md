# Audit an existing skill

An Audit checks a skill folder that already exists — the user's own, or a third party's from a marketplace, a plugin or a colleague — against the same rules a Build enforces. It reuses the Build steps in `SKILL.md` by number. It reports **Findings** in chat and changes nothing on disk until the user consents to a fix.

## Findings

Each Finding has a location (`file:line`, or the folder), the rule it breaks, and a severity:

- **blocking** — a `high` or `critical` security result, an undeclared script reach, or a skill the spec validator rejects. A blocking Finding stops the Audit at that check.
- **fix** — a rule is broken: a leaked path, a description over 1024 characters, a missing Scripts section or Built-with table, a failed eval criterion.
- **note** — a judgement call: a no-op candidate, a writing-for-agents suggestion, an ablation delta near zero.

## Before the checks

1. Confirm the folder holds a `SKILL.md`. When it has none but several folders below it do, e.g. a plugin or a skills folder, follow "A folder of many skills" below.
2. Decide whose folder it is. A folder under the user's own skills folder or in their own repository is **theirs**. Anything else is **third-party**, e.g. a plugin cache under `~/.claude/plugins/`, a download, or a colleague's copy. When in doubt, ask. Fixes land in place only in the user's own folder.
3. Ask for source material, as in step 1. If the user has none, say that grounding will not be checked and that the with-and-without comparison (the ablation) in the quality evals is the evidence instead. Do not wait for material the user says they lack.

## Checks, cheapest first

Run them in this order. After a blocking Finding, stop, report and run no later check.

When there is no shell to run a script, do that check by reading the files instead, and name the script that did not run in the report. Hold the evals until the scan has run. Never report a check as run when it was not.

1. **Spec and leaks.**
   - Validate the skill with `skills-ref`, exactly as step 8 item 5 does. A validator error is blocking.
   - *Run* `scripts/make_dist.py <skill folder> --check`. It builds no zip. Each line it prints is a fix Finding.
2. **Security scan.** Run step 8's security scan, items 1–4, on the audited folder. Never run the audited skill's scripts yourself: read them. Blocking Findings end the Audit here. When `evals_hold` is true, finish checks 3–4 and then hold the evals until the user says go.
3. **Rules.** Check each rule from step 4 and step 9, and file one Finding per broken rule:
   - The description says what the skill does and when to use it, is written as directives, names its near-misses, and is at most 1024 characters.
   - The body is under 500 lines. It points at every script with *run* and at every reference with *read*.
   - A Scripts section exists whenever `scripts/` does, with one line per script naming what that script reaches.
   - *Read* [authoring-rules.md](authoring-rules.md) and check the skill against it, one Finding per broken rule at the severity it names.
   - The README has an Agent Skills standard section, a Built-with table and a License section. When the skill invokes a skill it does not bundle, it also has an "Other skills it calls" table.
4. **Wording.** Run step 6 (writing-for-agents) and step 7 (no-op strip) on the audited text, but report what they flag as note Findings instead of editing.
   - With source material, check that each gotcha traces back to the source. A correction in the source that has no gotcha is a fix Finding. Content that traces to nothing is a note.
5. **Evals.**
   - If `evals/trigger-evals.json` or `evals/quality-evals.json` is missing, draft it as in step 5 and show it to the user. Draft each quality scenario in full, with its seeded files, its prompt and its rubric criteria; a list of scenario names is not a draft. Writing the approved file is a fix, so it follows the rules in "Fixes".
   - Then run step 8's eval cost warning and eval items 1–4. The runners call the skill that is installed under its name. If the skill being audited is a copy, install that copy first, with the user's consent.
   - A trigger case that misses in any trial is a fix. A criterion that fails with the skill is a fix. A with-skill score no better than without is a note: the skill may be a no-op, or a capability the model now has. A bundled file that no run opened, found as in step 8 item 3, is a note.

## A folder of many skills

A folder with no `SKILL.md` of its own is a folder of skills. Every folder below it that holds a `SKILL.md` is one skill; a `SKILL.md` inside a skill belongs to that skill.

1. Check 1 on every skill: run `skills-ref validate` once per skill, and *run* `scripts/make_dist.py <folder> --check` once for the whole folder; each line it prints starts with the skill's path.
2. Check 2 on every skill at once: *run* `scripts/security_scan.py <folder>`. It prints `{"skills": [...]}`, one scan result per skill, each named by its path in the folder. Run the read-only script subagent once per skill.
3. Checks 3–4 on every skill that has no blocking Finding. A blocking Finding stops the checks for that skill only; the other skills go on.
4. Post the report with one heading per skill, and under each skill the **blocking**, **fix** and **note** groups from "Report". Mark each skill with a blocking Finding as excluded from evals.
5. Ask which of the remaining skills to run evals on, and wait for the answer. Do not offer the excluded skills. Draft missing evals only for the chosen skills.
6. Treat the chosen set as one plan for the eval cost warning: run the pilot for each chosen skill, add the run counts, the notional USD and the window use, and show one warning for the whole set. When the user chose more than one model (step 8, Models), the run counts and costs already include every model. Then wait for the go-ahead before running any of them.

## Report

Post the report in chat. For a folder of many skills, the report has one heading per skill, as in "A folder of many skills". Group the Findings under **blocking**, **fix** and **note**, one line each:

`<location> — <rule broken>`

After that, list the checks that did not run and why, e.g. held evals, a blocking stop, or no source material. Say that the security scan is best-effort, whatever it found: a clean scan is not proof that a skill is safe. Write nothing into the audited folder.

## Fixes

Offer the fixes one Finding at a time, blocking Findings first. Show each change and apply it only after the user says yes.

- **The user's own folder:** edit in place.
- **Third-party folder:** ask the user where the copy goes, copy the whole folder there, and fix the copy. The original stays untouched, so a plugin update cannot silently discard the fixes.

After each fix, re-run the check that raised the Finding.
