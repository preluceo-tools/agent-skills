<div align="center">

# grounded-skill-builder

### Build agent skills from what you actually know, then prove they work.

<img src="https://img.shields.io/badge/Claude%20Code-skill-b1b9f9?style=flat-square&labelColor=0d1117" alt="Claude Code skill" />
<img src="https://img.shields.io/badge/Agent%20Skills-spec%20valid-b1b9f9?style=flat-square&labelColor=0d1117" alt="Valid against the Agent Skills specification" />
<img src="https://img.shields.io/badge/Python-3-b1b9f9?style=flat-square&labelColor=0d1117" alt="Python 3" />
<img src="https://img.shields.io/badge/license-GPL%20v3%20%C2%B7%20CC%20BY%204.0-b1b9f9?style=flat-square&labelColor=0d1117" alt="GPL v3 and CC BY 4.0" />

</div>

This is an agent skill for Claude Code that builds other skills. It builds them from **source
material you supply**: a transcript of you doing the task, a runbook, review comments, or a session
in which you corrected the agent. It does not build them from what the model already knows. It then
checks whether the new skill works by running tasks with the skill loaded and without it.

Without source material the builder asks for some and writes nothing.

> [!NOTE]
> **Unofficial.** This project is not affiliated with, endorsed by, or supported by Anthropic.
> Claude and Claude Code are named here only to say which tool this skill runs in.

> [!WARNING]
> **The evals cost usage.** The eval runners call the `claude` command-line tool once per prompt,
> per trial and per condition, and once more for each grade. A full run of one skill can take many
> dozens of calls on your Claude account. See [What it touches](#what-it-touches).

---

## Contents

- [What it does](#what-it-does)
- [Install](#install) · [Use](#use)
- [Other skills it calls](#other-skills-it-calls)
- [What it touches](#what-it-touches)
- [Does it work? One measured build](#does-it-work-one-measured-build)
- [Files](#files)
- [Agent Skills standard](#agent-skills-standard)
- [Built with](#built-with)
- [Credits](#credits)
- [Disclaimer](#disclaimer) · [License](#license)

---

## What it does

1. **Asks for source material** and reads all of it. For Claude Code sessions, a script extracts
   only the messages you typed from the transcripts, because that is where your corrections are.
2. **Mines the source**. It finds the job, the phrases that should start the skill and the
   near-misses where it must stay quiet. Every correction becomes a *gotcha*. Steps that must come
   out the same every time become scripts. Wherever your source and your request disagree, you
   decide.
3. **Asks where the skill installs**: for you (`~/.claude/skills/<name>/`) or for one project
   (`<project>/.claude/skills/<name>/`).
4. **Drafts the skill**: `SKILL.md`, plus `references/` for material only some cases need, and
   `scripts/` and `assets/`. Each script and template gets one runnable smoke check.
5. **Drafts two eval files for your approval**. Trigger evals are 5 prompts that should start the
   skill and 5 that should not. Quality evals are about 5 scenarios, each with seeded files and a
   rubric.
6. **Tightens the text** with the `writing-for-agents` skill (see
   [Other skills it calls](#other-skills-it-calls)). Then a fresh subagent **strips no-ops**:
   sentences that don't change what the agent does.
7. **Runs the evals** on the final text. Each trigger case runs 3 times. Each quality scenario runs
   with and without the skill, and a grader scores the runs without knowing which is which. Failures
   are fixed and re-run, or explained to you. Then it **validates the skill** with the validator of
   the [Agent Skills specification](https://agentskills.io/specification).
8. **Writes a README** for every skill, shared or not, with an "Agent Skills standard" section, a
   "Built with" section and a License section. If you share the skill, it also **zips it**. It
   refuses to build the zip while any file names a path from your machine.

---

## Install

Copy the `grounded-skill-builder` folder into your personal skills folder:

```text
~/.claude/skills/grounded-skill-builder/
```

On Windows that is `%USERPROFILE%\.claude\skills\grounded-skill-builder\`.

## Use

Ask in your own words and hand over the material, for example:

- "Make a skill out of this session so you don't repeat my corrections."
- "Here is our runbook for rotating the certificates. Turn it into a skill."

---

## Other skills it calls

| Skill | When | Where it comes from | License |
|---|---|---|---|
| `writing-for-agents` | Step 6, on the drafted `SKILL.md` and every `references/` file | [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock | MIT |

The builder calls it by name with the Skill tool. It is not bundled; install it yourself if you want
the step. If it is not installed, the builder says so and skips the step.

---

## What it touches

| Script | Touches |
|---|---|
| `scripts/extract_user_turns.py` | Reads the transcript files it is given; nothing else. |
| `scripts/run_trigger_evals.py`, `scripts/run_quality_evals.py` | Write run folders into a new temporary folder (or `--out`). Call the `claude` CLI, which uses your Claude account and usage. Shell commands are blocked in every run; quality runs may edit files inside their own run folder. |
| `scripts/make_dist.py` | Reads the skill folder; writes one zip into the dist folder. |
| `skills-ref` (not bundled) | Reads the skill folder. If it is not installed, `uvx` downloads it from github.com and pypi.org. |

---

## Does it work? One measured build

Every figure below comes from one real build: the `to-checklist` skill, which turns work to verify or
do by hand into an offline HTML checklist. It was built from two projects, with Claude Opus 5.5 in
Claude Code. Runs that ended in an API error (usage limit) or were refused file access say nothing
about the skill. 15 such runs were discarded, and none is counted below.

### Trigger evals: does the skill start when it should?

| | Runs | Correct |
|---|---|---|
| Should start (5 prompts) | 25 | **25** |
| Should stay quiet (5 prompts) | 25 | **25** |

These show only that the skill starts. A skill that is not loaded cannot start, so trigger evals
cannot compare with and without.

### Quality evals: is the result better with the skill?

Five scenarios, 2 runs per scenario and condition. A separate grader, which did not know the
condition, scored each run against a rubric of 6 to 10 points.

| Scenario | With skill | Without skill |
|---|---|---|
| Test a settings dialog from its changelog | 18/20 | 4/20 |
| Verify mail after a domain move (technical terms) | 20/20 | 6/20 |
| Progress checklist from four tickets | 20/20 | 13/20 |
| Handle results pasted back by the user | 12/12 | 7/12 |
| Test a Blender add-on with a test scene | 18/20 | 8/20 |
| **All** | **88/92 (96 %)** | **38/92 (41 %)** |

What changed in the output, counted over the runs whose rubric asked for it:

| Observation | With skill | Without skill |
|---|---|---|
| Wrote the requested HTML checklist | 8 of 8 runs | 0 of 8 (wrote Markdown instead) |
| Light/dark button on the page | 8 of 8 | 0 of 8 |
| Multiline comment box per item | 6 of 6 | 0 of 6 |
| Plain wording a newcomer can follow | 6 of 6 | 0 of 6 |
| Changed ticket files it was only meant to read | 0 of 4 | 1 of 4 |

### What the evals found

- **A real defect.** In one fixture run, the page's Setup section came out empty because the agent
  had written a field in a shape the template did not read. The trigger evals could not have found
  this. After the fix, re-runs of the two affected scenarios scored **48/50 (96 %)**, and the Setup
  section was correct in every run.
- **One remaining weakness.** In 2 of 5 re-runs, one check described its expected result with an
  "and" (e.g. "the count reads 6 again, and the edge is sharp"). The grader counted that as two
  outcomes.
- **Grader noise.** The grader failed 1 of the 92 points although the page met the criterion, which
  was checked by hand.

> [!NOTE]
> **How far these numbers go.** They cover one skill, one model, and 2 runs per scenario and
> condition. They show a large, consistent difference, not a precise size. The baseline switches
> off **all** skills, not only the one under test; no other installed skill was about checklists.
> The grader is a Claude model too. It sees only the files and the final message, never the
> condition.

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The steps the agent follows. |
| `references/grounding-rules.md` | The rules behind each step, with sources, and the formats of both eval files. |
| `scripts/extract_user_turns.py` | Prints only what the user typed in Claude Code transcripts. |
| `scripts/run_trigger_evals.py` | Runs the trigger evals and reports which prompts started the skill. |
| `scripts/run_quality_evals.py` | Runs the quality evals with and without the skill and grades each run blind. |
| `scripts/make_dist.py` | Zips a finished skill; refuses while any file names a path or the user of this machine. |
| `scripts/evalkit.py` | Shared code for the two eval runners. |
| `evals/trigger-evals.json` | Trigger evals for this builder itself. |
| `LICENSE`, `LICENSE-docs` | The license texts, see [License](#license). |

---

## Agent Skills standard

The skill follows the open [Agent Skills specification](https://agentskills.io/specification). It is
a folder with a `SKILL.md` whose frontmatter `name` matches the folder name. The `description` is
within 1024 characters and the body is well under the recommended 500 lines. The `scripts/` and
`references/` folders are linked one level deep from `SKILL.md`. It passes the specification's own
validator:

```text
skills-ref validate <skills folder>/grounded-skill-builder
```

The eval runners call the `claude` command-line tool, so the full build process needs Claude Code.

---

## Built with

**Nothing has to be downloaded beyond Claude Code and Python.** The scripts use only the Python
standard library.

| Component | What the tool uses it for | Where it comes from | License |
|---|---|---|---|
| [Claude Code](https://www.anthropic.com/claude-code) | Runs the builder; its command-line tool runs the eval prompts and the grader | Anthropic; needs a Claude subscription or API account | **Commercial** |
| [Python 3](https://www.python.org/) | Runs the scripts | python.org, or your system's package manager | [PSF License](https://docs.python.org/3/license.html), free |
| Python standard library: `argparse`, `json`, `subprocess`, `concurrent.futures`, `hashlib`, `os`, `re`, `tempfile`, `zipfile`, `getpass` | Command-line options, reading transcripts and eval files, calling `claude`, running evals in parallel, hashing seeded files, building the zip | Ships with Python | PSF License, free |
| Optional: the `writing-for-agents` skill | Tightens the wording of the skill being built | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT, free |
| Optional: [uv](https://docs.astral.sh/uv/) | Runs skills-ref without installing it | Its site, or your package manager | MIT or Apache-2.0, free |
| Optional: [skills-ref](https://github.com/agentskills/agentskills) | Validates each skill it builds against the Agent Skills specification | Installed, or fetched by `uvx` on each run | Apache-2.0, free |

Claude Code is the only commercial component. Without the optional skill the builder says so and
skips that step. Without uv it checks the specification's rules by hand.

---

## Credits

- **Sources of the rules.** The rules in `references/grounding-rules.md` are distilled, in our own
  words, from two public talks. No transcript text is included.
  - IBM Technology, [*5 Best Practices for Building AI Agent Skills*](https://www.youtube.com/watch?v=qYNs80FKIVc) (YouTube)
  - Philipp Schmid (Google DeepMind), [*Don't Ship Skills Without Evals*](https://www.youtube.com/watch?v=0vphxNt4wyk), AI Engineer (YouTube)
- **Matt Pocock's [skills](https://github.com/mattpocock/skills)** (MIT). The builder calls his
  `writing-for-agents` skill (see [Other skills it calls](#other-skills-it-calls)). The builder's own
  design was also worked out with his `grill-with-docs` skill.
- **The [Agent Skills specification](https://agentskills.io/specification)** and its `skills-ref`
  validator, which the builder checks every skill against.

---

## Disclaimer

This skill is provided **"as is", without warranty of any kind**, express or implied, including but
not limited to the warranties of merchantability, fitness for a particular purpose and
non-infringement. You use it entirely at your own risk.

The author and contributors are not liable for any claim, damage or other loss arising from its use
or from being unable to use it. That includes usage charges on your Claude account, files an agent
changes, and skills that do not behave as their evals suggest. Reading what the builder writes, and
what the scripts run, is your responsibility.

The licenses below say the same in their own terms (GPL v3, sections 15 and 16; CC BY 4.0,
section 5). Where this summary and a license differ, the license applies.

## License

© 2026 preluceo

**The code**, meaning the scripts in `scripts/`, is licensed under the
[GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html) (see [`LICENSE`](LICENSE)). You may use,
study, change and share it. If you distribute a modified version, it has to stay free under the same
terms.

**The prose**, meaning `SKILL.md`, the reference file, the eval files and this manual, is licensed
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see [`LICENSE-docs`](LICENSE-docs)).
You may share and adapt it for any purpose if you give credit.

*This summary is not a license. The linked texts are the actual terms.*
