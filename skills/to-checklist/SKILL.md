---
name: to-checklist
description: Checklist for work the user verifies or does by hand — a local, offline HTML page of Checks (pass / fail / skip, multiline comment) and/or Tasks (open / done / waiting / dropped), whose results come back as fixed-format text. Use when the user asks for a checklist or manual checks (QA, "test this by hand", after an AFK ticket run), a progress checklist for human-only tickets, or a re-test after fixes, and when they paste text starting "## Checklist results". Offers a Test Fixture (a purpose-built scene or document) when checks run inside an application that opens documents. Not for automated tests, CI, code review, or a to-do list answered in chat.
---

# to-checklist

A **Checklist** is one self-contained HTML file. It holds **Checks** (things the user tries and judges), **Tasks** (things the user does), or both in separate sections. The user works through it offline and hands back the **Paste-back**: fixed Markdown listing every item with its state and comment.

## 1. Draft the items

Draft from whatever describes the work: the conversation, a spec, tickets, a handoff or changelog, a finished AFK run (each ticket's acceptance criteria and what it changed), a wayfinder map, or a pasted list.

- **Check**: one manual verification with exactly one observable **Expected** result. If the Expected needs an "and", make two Checks. IDs `CHK01`, `CHK02`, …
- **Task**: one thing to do. From a ticket, its ID is `T` + the ticket number (`T05`) and it carries `ticket`. Optional `due` (a date) and `after` (Task IDs it follows).
- **Steps**: the exact menu path, button or shortcut, in order, one action per Step. Mark every label you have not confirmed with `(verify label)`, or ask.
- **Use**: per Check, the objects to select or the file to open.
- At most about 25 Checks per Checklist.
- **Order**: the page reads Setup, then Checks, then Tasks. Anything that must come first goes in Setup.
- **Not a Task**: a step that acts on the Check outcomes (publish, release, tag, announce). Leave it out; propose it in step 4 once every failure is accounted for.
- **Code**: write commands, file names and keys in `backticks`. Never write `<code>` tags; the page shows HTML as text.

Show the drafted list (ID, title, one-line Expected or goal).

Done when the user has confirmed or edited it.

## 2. Offer a Test Fixture

Ask only when Checks run inside an application that opens documents: "Create a Test Fixture? The Checks will then point at its elements by name." On yes, read [references/fixtures.md](references/fixtures.md) and follow it. On no, and for GUI, CLI or web testing, the Steps say what to press and in what order.

Done when every Check's `use` names an element that exists and `setup.fixtures` has one row per element, or no fixture was wanted.

## 3. Write the Checklist

1. Copy [assets/checklist.html](assets/checklist.html) to `<project>/checklists/<topic>-checklist.html`. Replace only the object between `/*DATA-START*/` and `/*DATA-END*/`; the comment above it lists every field. The rest of the page, including the Paste-back format and the light/dark toggle, stays as it is.
2. Write every title, Step, Expected, intro and Setup line for a **newcomer**: someone who knows neither the project nor the technical field.
   - Say what to look at and what it should look like, not how it works inside.
   - Explain each unavoidable technical term in a few plain words where it first appears, e.g. "the Spam folder (where suspected junk goes)".
   - Use the terms from the project's `CONTEXT.md`.

   Then re-read each item as the newcomer and rewrite anything that needs background knowledge.
3. In `intro`, explain the effort and every term the items rely on.
4. Open the file for the user. Tell them to press **Copy results** and paste the text, or **Save results**, which downloads `<topic>-results.md`, usually into the Downloads folder rather than next to the page. Ask where it landed.
5. If the thing under test can write a log, switch the log on, tell the user where it goes, and read it together with the results.

Done when the page is open in the user's browser, every item reads plainly to the newcomer, and every Expected holds exactly one outcome.

## 4. When the results come back

The text starts with `## Checklist results:`. Each line reads `- <ID> <state> - <title>`, followed by comment lines `  > …`.

- **`(comment missing)`** on a `fail`, `waiting` or `dropped` item: ask the user what they saw or why.
- **Failed Checks**: fix them in this session. When there are many, or they are out of scope, offer one issue per failure in the project's issue tracker with `Status: needs-triage`.
- **Tasks from tickets**: the tickets stay the source of truth. Propose the `Status:` change for each ticket and write the changes once the user confirms.
- **Re-test**: after fixes, write `<topic>-checklist-r2.html` (then `-r3`, …). It holds the failed Checks plus every Check the fix could affect, under their original IDs.
- **Progress refresh**: regenerate from the current tickets, keeping the Task IDs.

Done when every item in the Paste-back is accounted for: passed, fixed, filed, confirmed, or reported as not done.
