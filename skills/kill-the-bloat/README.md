<div align="center">

# kill-the-bloat

### Trim what Claude Code sends with every request, by answering Keep or Disable.

<img src="https://img.shields.io/badge/Claude%20Code-skill-b1b9f9?style=flat-square&labelColor=0d1117" alt="Claude Code skill" />
<img src="https://img.shields.io/badge/Agent%20Skills-spec%20valid-b1b9f9?style=flat-square&labelColor=0d1117" alt="Valid against the Agent Skills specification" />
<img src="https://img.shields.io/badge/evals-partly%20run-b1b9f9?style=flat-square&labelColor=0d1117" alt="Evals partly run" />
<img src="https://img.shields.io/badge/license-GPL%20v3%20%C2%B7%20CC%20BY%204.0-b1b9f9?style=flat-square&labelColor=0d1117" alt="GPL v3 and CC BY 4.0" />

</div>

This is an agent skill for Claude Code. It lists the tools, skills, plugins, MCP servers and
connectors your session has loaded, shows each with a 0-10 generic usefulness score, asks you to keep
or disable it, and writes the result into your `settings.json` with a script. You never edit the JSON
by hand.

> [!NOTE]
> **Unofficial.** This project is not affiliated with, endorsed by, or supported by Anthropic.
> Claude and Claude Code are named here only to say which tool this skill runs in.

---

## Contents

- [What it does](#what-it-does)
- [Install](#install) · [Use](#use)
- [Does it work? What was and was not measured](#does-it-work-what-was-and-was-not-measured)
- [Files](#files)
- [Built with](#built-with)
- [Credits and sources](#credits-and-sources)
- [Disclaimer](#disclaimer) · [License](#license)
- [Version history](#version-history)

---

## What it does

- Reads the tools, skills, plugin skills, MCP servers and connectors that this session has loaded.
- Shows each with a **score from 0 to 10**, a one-line purpose and a daily-use note. The scores are
  generic research for a typical user, not a measurement and not your preference. Items marked `low`
  confidence in `references/scores.md` are reasoned estimates.
- Asks Keep or Disable, grouped so that one switch covers a whole feature where Claude Code offers one.
- Writes the disable flags, `permissions.deny` entries and `skillOverrides` with a script. It shows
  the diff first and writes only after you confirm. A `.bak` copy is made before every write.
- **Never offered:** Bash, Read, Edit, Write, Grep, Glob, Skill, ToolSearch, Agent and
  AskUserQuestion. The script refuses them.

---

## Install

Copy the `kill-the-bloat` folder into your personal skills folder:

```text
~/.claude/skills/kill-the-bloat/
```

On Windows that is `%USERPROFILE%\.claude\skills\kill-the-bloat\`. To limit the skill to one project,
put it in `<project>/.claude/skills/kill-the-bloat/` instead. Python 3 must be on the PATH.

## Use

Ask in your own words, for example: "Cut my Claude Code context, help me disable tools I never use."
The skill then:

1. asks which `settings.json` to write (user or project) and for your current `/context` total,
2. inventories what this session has loaded,
3. asks Keep or Disable per item,
4. shows the diff and writes it only after you confirm,
5. tells you to restart Claude Code and compare `/context`.

To undo, copy the `.bak` file back over `settings.json`.

---

## Does it work? What was and was not measured

Everything below was run on **Claude Sonnet only**, with the quality evals in plan-only form (see
[Known limits](#known-limits)).

### Done

| Check | Result |
|---|---|
| Agent Skills validator (`skills-ref validate`) | `Valid skill` |
| Script self-check (`scripts/test_apply_settings.py`) | Prints `ok`: merge, `.bak` copy, and refusal of protected tools, scoped rules, unknown flags and bad modes |
| Static security scan (Cisco skill-scanner) | One note (missing license), since resolved. Best effort, not proof |
| Trigger evals, prompts that should start the skill (5) | Started in every counted trial |
| Trigger evals, prompts that should stay quiet (5) | 15 runs, none started the skill |
| Quality evals, with the skill (5 scenarios, 2 runs each) | 74 of 74 rubric points |

The trigger runner marked many runs invalid, because the skill's own file reads hit a permission
prompt after it had started. The starts were therefore counted by hand from the transcripts. One
prompt was reworded and re-run separately (3 of 3).

### Not done

- **No baseline.** The quality evals were never run without the skill, so there is **no measured
  difference** between using the skill and not using it. The run without the skill failed every time:
  the agent tried to hand-edit `.claude/settings.json`, which Claude Code blocks. The 74/74 shows that
  the skill produces a correct plan, not that it beats the alternative.
- **The scripted write was never part of an eval.** The eval runner blocks shell tools, so the agent
  only wrote `plan.json`. `apply_settings.py` was tested separately by its own self-check, not by
  an agent in a live session.
- **Not re-run after the last edits.** The scores and the wording were adjusted after the eval runs.
- **One model.** Opus, Haiku and other models were not tried.
- **No measured token saving.** Nobody has compared `/context` before and after on a real
  installation with this skill. The figures in `references/scores.md` come from published sources,
  and many tools are deferred behind ToolSearch, so real savings can be smaller.
- **Scores are mostly unverified.** Of the 57 rows in `references/scores.md`, 20 have `low` confidence (no source,
  a reasoned estimate). Only about 6 skills and a few tools have independent sources. The refresh pass
  (re-searching the `low` rows) has not been run.
- **No review by a second person.** Nobody other than the author has checked the scores or the
  plan-only eval design.

### Known limits

- Higher settings scopes win for flags; `deny` lists combine across files, so a user-level deny still
  applies in every project.
- `settings.json` and `settings.local.json` are separate files in one scope. The skill writes only
  the one you pick.
- That a *scoped* rule such as `Bash(rm *)` keeps the tool definition in context (and so saves
  nothing) is stated only by the source article, not by Anthropic's documentation. The skill refuses
  scoped rules for this reason.
- Denying ExitPlanMode probably breaks plan mode. This is reasoned, not tested.

> [!NOTE]
> **How far these numbers go.** One skill, one model, 2 runs per scenario, no baseline, graded
> against a rubric the author wrote. They show that the plans come out right in a controlled
> setting. They do not show that the skill is better than doing it by hand.

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The 5-step Q&A the agent follows. |
| `references/scores.md` | Scores, notes and source links for each item; refreshable on request. |
| `scripts/apply_settings.py` | Merges a plan into `settings.json`, prints the diff, writes with `--write`. |
| `scripts/test_apply_settings.py` | Self-check for the script: `python scripts/test_apply_settings.py` prints `ok`. |
| `evals/trigger-evals.json` | Test prompts: five that should start the skill and five that should not. |
| `evals/quality-evals.json` | Five scenarios, each with a seeded settings file and a rubric. |
| `LICENSE`, `LICENSE-docs` | The license texts, see [License](#license). |

---

## Built with

**Nothing has to be downloaded** except Python 3, if it is not installed yet.

| Component | What the tool uses it for | Where it comes from | License |
|---|---|---|---|
| [Claude Code](https://www.anthropic.com/claude-code) | Runs the skill; its `settings.json` is the file that gets edited | Anthropic; needs a Claude subscription or API account | **Commercial** |
| [Python 3](https://www.python.org/) standard library: `difflib`, `json`, `shutil`, `sys`, `pathlib` | `scripts/apply_settings.py` merges the plan and prints the diff | [python.org](https://www.python.org/downloads/) | Free ([PSF license](https://docs.python.org/3/license.html)) |
| Python 3 standard library for the self-check: `json`, `subprocess`, `tempfile`, `pathlib`, `sys` | `scripts/test_apply_settings.py` | Same | Free |

Used while building, not needed to run the skill:

| Component | What it was used for | Where it comes from | License |
|---|---|---|---|
| [Cisco skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) | Static security scan before the evals | GitHub | Free (open source) |
| [skills-ref](https://github.com/agentskills/agentskills) | Agent Skills validator | GitHub | Free (open source) |

Claude Code is the only commercial component.

---

## Credits and sources

- **The name of the skill is inspired by** Matt Pocock's article
  [How to kill the bloat in Claude Code's system prompt](https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt).
- **The idea and the first score list** come from the same article.
  The article is one author's own list and token measurements. The skill turns it into an interactive
  Q&A and a script.
- **How Claude Code settings behave** (`permissions.deny`, `skillOverrides`, the `disable*` flags,
  scopes) was checked against [Anthropic's Claude Code documentation](https://code.claude.com/docs).
  Where only the article says something, `references/scores.md` says so.
- **The scores** combine the article, the documentation and a few third-party skill reviews. Each row
  in `references/scores.md` names its sources, or says `reasoned` when it has none.
- The skill was built, and its evals were run, with the
  [grounded-skill-builder](../grounded-skill-builder/) skill, and edited with
  `writing-for-agents` from [Matt Pocock's skills](https://github.com/mattpocock/skills) (MIT).

---

## Disclaimer

This skill is provided **"as is", without warranty of any kind**, express or implied, including but
not limited to the warranties of merchantability, fitness for a particular purpose and
non-infringement. You use it entirely at your own risk.

The skill **edits your Claude Code `settings.json`**. It writes a `.bak` copy first and only after
you confirm the diff, but you are responsible for what you disable. Disabling a tool can break a
workflow that needs it, and the scores are generic, not advice for your setup. The author and
contributors are not liable for any claim, damage or other loss arising from its use or from being
unable to use it.

The licenses below say the same in their own terms (GPL v3, sections 15 and 16; CC BY 4.0,
section 5). Where this summary and a license differ, the license applies.

## License

© 2026 preluceo

**The code**, meaning `scripts/apply_settings.py` and `scripts/test_apply_settings.py`, is licensed
under the [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html) (see [`LICENSE`](LICENSE)). You may
use, study, change and share it. If you distribute a modified version, it has to stay free under the
same terms.

**The prose**, meaning `SKILL.md`, `references/scores.md`, the eval files and this manual, is
licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see
[`LICENSE-docs`](LICENSE-docs)). You may share and adapt it for any purpose if you give credit.

*This summary is not a license. The linked texts are the actual terms.*

---

## Version history

Newest first.

### 0.1.0 (2026-10-07)

- First release: inventory, 0-10 scores, Keep or Disable Q&A, diff, and a scripted write with a
  `.bak` backup.
