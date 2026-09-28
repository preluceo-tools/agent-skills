<div align="center">

# to-checklist

### Turn what you have to check by hand into a checklist page, and hand the results back.

<img src="https://img.shields.io/badge/Claude%20Code-skill-b1b9f9?style=flat-square&labelColor=0d1117" alt="Claude Code skill" />
<img src="https://img.shields.io/badge/Agent%20Skills-spec%20valid-b1b9f9?style=flat-square&labelColor=0d1117" alt="Valid against the Agent Skills specification" />
<img src="https://img.shields.io/badge/runs-offline-b1b9f9?style=flat-square&labelColor=0d1117" alt="Runs offline" />
<img src="https://img.shields.io/badge/license-GPL%20v3%20%C2%B7%20CC%20BY%204.0-b1b9f9?style=flat-square&labelColor=0d1117" alt="GPL v3 and CC BY 4.0" />

</div>

This is an agent skill for Claude Code. It turns the work you have to verify or do by hand into a
checklist page that runs offline in your browser. When you are done, the agent reads your results
back, fixes what failed, and updates your tickets.

> [!NOTE]
> **Unofficial.** This project is not affiliated with, endorsed by, or supported by Anthropic.
> Claude and Claude Code are named here only to say which tool this skill runs in.

---

## Contents

- [What it does](#what-it-does)
- [Install](#install) · [Use](#use)
- [The results](#the-results)
- [Other skills it works with](#other-skills-it-works-with)
- [Files](#files)
- [Built with](#built-with)
- [Credits](#credits)
- [Disclaimer](#disclaimer) · [License](#license)

---

## What it does

- **Checks** are things you try and judge. You mark each one *pass*, *fail* or *skip*, or leave it
  *untested*, and you can write a comment of several lines.
- **Tasks** are things you have to do. You mark each one *open*, *done*, *waiting* or *dropped*. A
  Task can carry a due date and the Tasks it should follow.
- A checklist can hold Checks, Tasks or both. It is a single HTML file with no external resources.
  It follows your system's light or dark setting and has a button to switch between the two. Your
  marks stay in the browser for that page.
- When the checks run inside an application that opens documents (e.g. a 3D modeller, an image
  editor, a word processor), the skill offers to build a **Test Fixture**. That is a sample document
  made for the checks, with every element named, so each check can tell you exactly what to select.
- When you finish, **Copy results** puts the results on the clipboard and **Save results** downloads
  them as a Markdown file. Hand that text to the agent. It fixes what failed, files issues, or
  proposes status changes for your tickets.

---

## Install

Copy the `to-checklist` folder into your personal skills folder:

```text
~/.claude/skills/to-checklist/
```

On Windows that is `%USERPROFILE%\.claude\skills\to-checklist\`. To limit the skill to one project,
put it in `<project>/.claude/skills/to-checklist/` instead.

## Use

Ask in your own words, for example:

- "Make me a checklist of what I still have to test by hand."
- "Progress checklist for the tickets only I can do, with the due dates."
- "Re-test checklist for the two fixes."

The agent shows you the drafted items first, and you correct them. It then writes
`<project>/checklists/<topic>-checklist.html` and opens it. When you are done, paste the results
back, or tell the agent where the saved file is. Browsers usually save it into your Downloads folder.

---

## The results

The results always look like this:

```text
## Checklist results: <topic> (<date>)
Environment: <where you tested>
Checks: 5 pass, 1 fail, 0 skip, 0 untested

### Checks
- CHK01 pass - <title>
- CHK02 fail - <title>
  > what you saw instead
```

> [!TIP]
> A *fail*, *waiting* or *dropped* item without a comment is marked `(comment missing)`, and the
> agent will ask you what happened. Write the comment on the page to save that round trip.

---

## Other skills it works with

**to-checklist calls no other skill.** It is complete on its own.

It does follow the working conventions of [Matt Pocock's skills](https://github.com/mattpocock/skills)
(MIT), when a project uses them:

| Convention | Set up by | What to-checklist does with it |
|---|---|---|
| Local issue tracker: one Markdown file per ticket, each with a `Status:` line | `setup-matt-pocock-skills` | Turns human-only tickets into Tasks, and proposes `Status:` changes after the results come back |
| Triage label `needs-triage` | `setup-matt-pocock-skills` | Marks the issues it files for failed Checks |
| Glossary in `CONTEXT.md` | `domain-modeling`, `grill-with-docs` | Uses the project's own terms in the checklist |
| Tickets with acceptance criteria, and `wayfinder` maps | `to-tickets`, `wayfinder` | Drafts Checks from each ticket's acceptance criteria, e.g. after an unattended (AFK) agent run |

None of these is required. Without them, the skill drafts the checklist from the conversation, a
spec, a changelog or a pasted list.

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The instructions the agent follows. |
| `references/fixtures.md` | How the agent builds and describes a Test Fixture. Read only when you want one. |
| `assets/checklist.html` | The page template. The agent fills in only its data block. |
| `evals/trigger-evals.json` | Test prompts: five that should start the skill and five that should not. |
| `evals/quality-evals.json` | Test scenarios, each with seeded files and a rubric, run with and without the skill. |
| `LICENSE`, `LICENSE-docs` | The license texts, see [License](#license). |

---

## Built with

**Nothing has to be downloaded.** The skill is a set of text files. The checklist page uses only
features built into every current browser.

| Component | What the tool uses it for | Where it comes from | License |
|---|---|---|---|
| [Claude Code](https://www.anthropic.com/claude-code) | Runs the skill: drafts the items, writes the page, reads the results | Anthropic; needs a Claude subscription or API account | **Commercial** |
| A current web browser, e.g. [Firefox](https://www.mozilla.org/firefox/), [Chrome](https://www.google.com/chrome/), [Edge](https://www.microsoft.com/edge) | Opens the checklist page | Usually already installed | Free |
| Browser features: [Web Storage](https://developer.mozilla.org/docs/Web/API/Web_Storage_API), [Clipboard API](https://developer.mozilla.org/docs/Web/API/Clipboard_API), [Blob](https://developer.mozilla.org/docs/Web/API/Blob), [`prefers-color-scheme`](https://developer.mozilla.org/docs/Web/CSS/@media/prefers-color-scheme) | Keep your marks, copy the results, save the results file, follow the system theme | Built into the browser | Part of the browser |
| Optional: a way for the agent to drive your application, e.g. an [MCP](https://modelcontextprotocol.io/) server or the application's own scripting | Builds a Test Fixture directly in the application | Depends on the application | Depends on the application |

Claude Code is the only commercial component. Without the optional component the skill still works:
the agent writes build instructions for the Test Fixture into the checklist, and you build it
yourself.

---

## Credits

- **[Matt Pocock's skills](https://github.com/mattpocock/skills)** (MIT) supply the issue tracker,
  triage and glossary conventions this skill follows (see
  [Other skills it works with](#other-skills-it-works-with)). The skill's design was worked out with
  his `grill-with-docs` skill.
- The skill was built, and its evals were run, with the grounded-skill-builder skill.

---

## Disclaimer

This skill is provided **"as is", without warranty of any kind**, express or implied, including but
not limited to the warranties of merchantability, fitness for a particular purpose and
non-infringement. You use it entirely at your own risk.

The author and contributors are not liable for any claim, damage or other loss arising from its use
or from being unable to use it. That includes checks the checklist missed, files or tickets an agent
changes, and anything done with the results. Deciding what counts as tested is your responsibility.

The licenses below say the same in their own terms (GPL v3, sections 15 and 16; CC BY 4.0,
section 5). Where this summary and a license differ, the license applies.

## License

© 2026 preluceo

**The code**, meaning the page template `assets/checklist.html` and its script, is licensed under
the [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html) (see [`LICENSE`](LICENSE)). You may use,
study, change and share it. If you distribute a modified version, it has to stay free under the same
terms.

**The prose**, meaning `SKILL.md`, the reference file, the eval files and this manual, is licensed
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see [`LICENSE-docs`](LICENSE-docs)).
You may share and adapt it for any purpose if you give credit.

*This summary is not a license. The linked texts are the actual terms.*
