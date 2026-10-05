# Authoring rules

The checks step 4 and Audit rule 3 apply to a skill's own files. Every rule is tagged [S7], Anthropic's *Skill authoring best practices* (see [grounding-rules.md](grounding-rules.md)). Report each broken rule as one Finding: location, rule, `fix` or `note`.

The spec validator checks name and description limits, not these rules. It prints `Valid skill` for a name containing "claude" and for a description containing `<b>`. Apply the reserved-word and XML-tag rules by hand, and never tell the user the validator covers them.

## fix

Break discovery, portability or loading.

- Description is third person ("Builds…", "Checks…"), never "I can…" or "You can…". It is injected into the system prompt. [S7]
- Name has no reserved word ("anthropic", "claude") and no XML tag; description has no XML tag. [S7]
- Paths in `SKILL.md` and `references/` use forward slashes, even for Windows. [S7]
- Every reference file is linked from `SKILL.md` directly, so none is reachable only through another file. A nested file is read partially. [S7]
- Scripts that need a CLI or network host have `compatibility` in the frontmatter saying so. [S7]

## note

Advice; the skill works without it.

- A reference file over 100 lines opens with a Contents list. [S7]
- Name is a gerund or noun phrase that tells skills apart; not `helper`, `utils`, `documents`; same pattern as the user's other skills. [S7]
- One term per concept in every file. [S7]
- No instruction that expires with a date ("before August"). [S7]
- Where several ways work, the body names a default and one escape hatch, not a menu. [S7]
- A fixed output shape comes with a template. [S7]
- Whatever the skill asks the agent to write (description, gotcha, Scripts line) comes with one example. [S7]
- An MCP tool is written `Server:tool`, or the agent may report "tool not found". [S7]
- Every constant in a script (timeout, retry count, default) has a one-line comment saying why. [S7]
- File names say what the file holds: `form_validation_rules.md`, not `doc2.md`. [S7]
- A bundled file that no run opened (step 8 item 3, Audit evals) is unneeded or badly signalled in the body. [S7]

## Worked examples

From the measured `to-checklist` build ([S3]). Match their shape, not their wording.

**Description** — what, when, near-misses, third person:

> Checklist for work the user verifies or does by hand — a local, offline HTML page of Checks (pass / fail / skip, multiline comment) and/or Tasks (open / done / waiting / dropped), whose results come back as fixed-format text. Use when the user asks for a checklist or manual checks (QA, "test this by hand", after an AFK ticket run) … Not for automated tests, CI, code review, or a to-do list answered in chat.

**Gotcha** — an environment fact that defies a reasonable assumption, with the consequence:

> Write commands, file names and keys in `backticks`. Never write `<code>` tags; the page shows HTML as text.

**Scripts line** — names everything the file reaches. This build ships a template, not a script:

> `assets/checklist.html` is copied, never run by the agent; the page calls no network host and keeps its state in the browser's local storage.

**Trigger case** — a prompt a user would type:

> give me a manual QA checklist for the new settings dialog, pass/fail with comments

**Near-miss** — shares vocabulary, must stay silent:

> What's left on my to-do list for today? Just list it here.
