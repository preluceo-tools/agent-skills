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

It also **audits skills that already exist**: your own, or one you downloaded and are about to
install. See [Audit an existing skill](#audit-an-existing-skill).

> [!NOTE]
> **Unofficial.** This project is not affiliated with, endorsed by, or supported by Anthropic.
> Claude and Claude Code are named here only to say which tool this skill runs in.

> [!WARNING]
> **The evals cost usage.** The eval runners call the `claude` command-line tool once per prompt,
> per trial and per condition, and once more for each grade. A full run of one skill can take many
> dozens of calls on your Claude account. Before every eval run, the builder runs a small pilot, shows
> you the measured estimate (runs, notional USD, and your five-hour usage window now and after, with
> its reset in local time), and waits for your go-ahead. See [What it touches](#what-it-touches).

---

## Contents

- [What it does](#what-it-does) · [Audit an existing skill](#audit-an-existing-skill)
- [Install](#install) · [Use](#use) · [Tips from Anthropic](#tips-from-anthropics-guidance)
- [Other skills it calls](#other-skills-it-calls)
- [What it touches](#what-it-touches)
- [Eval status](#eval-status)
- [Does it work? One measured build](#does-it-work-one-measured-build)
- [The builder's own evals](#the-builders-own-evals)
- [Files](#files)
- [Agent Skills standard](#agent-skills-standard)
- [Built with](#built-with)
- [Credits](#credits)
- [Disclaimer](#disclaimer) · [License](#license)
- [Version history](#version-history)

---

## What it does

1. **Asks for source material** and reads all of it. For Claude Code sessions, a script extracts
   only the messages you typed from the transcripts, because that is where your corrections are.
2. **Mines the source**. It finds the job, the phrases that should start the skill and the
   near-misses where it must stay quiet. Every correction becomes a *gotcha*. Steps that must come
   out the same every time become scripts. Wherever your source and your request disagree, you
   decide. It then offers an optional **Baseline** pass (see below); the default is no.
3. **Asks where the skill installs**: for you (`~/.claude/skills/<name>/`) or for one project
   (`<project>/.claude/skills/<name>/`).
   If you accept the Baseline, the quality scenarios are drafted next and run without the skill
   only, after the cost estimate and your go-ahead. The rubric items that fail show what the skill
   must teach, and the draft covers those. It costs about half of a quality eval run.
4. **Drafts the skill**: `SKILL.md`, plus `references/` for material only some cases need, and
   `scripts/` and `assets/`. It checks the draft against the authoring rules (see
   [Agent Skills standard](#agent-skills-standard)). Each script and template gets one runnable
   smoke check.
5. **Drafts two eval files for your approval**. Trigger evals are 5 prompts that should start the
   skill and 5 that should not. Quality evals are about 5 scenarios, each with seeded files and a
   rubric. A checker then validates both files before you are asked to approve them: at least 5
   cases of each kind, unique ids, seeded files wherever a prompt names a file or folder, and 6 to
   10 rubric items per scenario. Both runners run the same check before any paid call.
6. **Tightens the text** with the `writing-for-agents` skill (see
   [Other skills it calls](#other-skills-it-calls)). Then a fresh subagent **strips no-ops**:
   sentences that don't change what the agent does.
7. **Scans the new skill for security problems** before any of its scripts run: a static scanner,
   a search for known payload shapes (hidden Unicode, download-and-run commands, credential reads),
   and a fresh read-only subagent that compares each script with what the skill declares it
   reaches. A high-severity finding stops the build until it is fixed. If the scanner cannot run,
   you get the cause and the fix, and the evals wait for your go-ahead. A clean scan is
   best-effort, not proof that a skill is safe.
8. **Runs the evals** on the final text, on the model in use or on the models you choose (e.g. Haiku,
   Sonnet), after showing you a cost estimate measured by a small pilot on each model, multiplied by the
   number of models, and waiting for your go-ahead. Each trigger case runs 3 times. Each quality scenario runs
   with and without the skill, and a grader scores the runs without knowing which is which. Failures
   are fixed and re-run, or explained to you. It also reads each run's transcript for the bundled
   files that were never opened and reports them. Then it **validates the skill** with the validator of
   the [Agent Skills specification](https://agentskills.io/specification).
9. **Writes a README** for every skill, shared or not, with an "Agent Skills standard" section, a
   "Built with" section and a License section. If you share the skill, it also **zips it**. It
   refuses to build the zip while any file names a path from your machine.

---

## Audit an existing skill

Point the builder at a skill folder and it runs the same checks a build does, cheapest first:

1. The Agent Skills validator, and a search for paths and the user name of your machine.
2. The security scan. A high-severity finding stops the audit here, before any eval runs. The
   audited skill's scripts are read, never run.
3. The rules for the description, the body, the Scripts section and the README sections, and the
   authoring rules (see [Agent Skills standard](#agent-skills-standard)).
4. `writing-for-agents` and the no-op strip, as suggestions only.
5. The evals, after the cost estimate and your go-ahead. A skill without evals gets drafts for your
   approval first.

It asks for source material. Without it, grounding is not checked, and the comparison with and
without the skill is the evidence instead.

The report goes to chat. Each finding names its location, the rule it breaks and a severity:
*blocking*, *fix* or *note*. Nothing is written into the audited folder. After the report, the
builder offers the fixes one at a time and applies each only when you agree. A skill that is not
yours, e.g. one in a plugin cache, is copied first to a folder you choose, and the fixes go into the
copy.

Point it at a folder that holds several skills, e.g. a plugin or your skills folder, and it runs
checks 1–4 on every skill and reports the findings skill by skill. A skill with a blocking finding
is left out of the evals; the others are not. It then asks which skills to run evals on, and shows
one cost estimate for the whole set before running any of them.

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
- "Audit my skill at `<skill folder>`."
- "Is this downloaded skill safe to install?"
- "Audit every skill in `<plugin folder>`."

---

## Tips from Anthropic's guidance

These two tips come from Anthropic's
[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
They are the source's advice for skill authors; the builder does not do either for you.

- **A copyable progress checklist.** For a skill with many steps, put a short checklist in it that
  the agent copies into its reply and ticks off as it goes. It keeps its place across a long run.
- **Share the skill with a teammate.** Ask someone to use it on a real task and report whether it
  started when expected and what it was missing.

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
| `scripts/evalcheck.py` | Reads the eval files it is given; nothing else. Both runners call it before any `claude` call. |
| `scripts/run_trigger_evals.py`, `scripts/run_quality_evals.py` | Write run folders into a new temporary folder (or `--out`). Call the `claude` CLI, which uses your Claude account and usage. Shell commands, web search and web fetch are blocked in every quality run, so a run without the skill cannot stall at a permission prompt for them. Quality runs may edit files inside their own run folder; runs with the skill may also read, and edit, files in your personal skills folder, where the skill under test is installed. With `--pilot`, they run a small slice, make one extra minimal `claude` call to read the five-hour usage window, and print a cost estimate for the full run. |
| `scripts/security_scan.py` | Reads the skill folder, or every skill in a folder of skills. Runs the Cisco skill-scanner, pinned to one version, through `uvx`, which downloads it from github.com and pypi.org on first use; only its static analyzers run, with no API key and no upload. |
| `scripts/test_scripts.py` | Checks the shared eval code on recorded output and runs `scripts/security_scan.py` on seeded folders in a temporary folder it deletes. No `claude` calls. |
| `scripts/make_dist.py` | Reads the skill folder; writes one zip into the dist folder. With `--check` it only reads. |
| `skills-ref` (not bundled) | Reads the skill folder. If it is not installed, `uvx` downloads a pinned commit of it from github.com and pypi.org. |

---

## Eval status

| Eval | Last run | Model | Status |
|---|---|---|---|
| Builder's trigger evals (16 prompts) | 2026-09-29 | Claude Opus 5.5 | Description unchanged since. Body and references have changed since this run. |
| Builder's quality evals (7 scenarios) | 2026-10-05 | Claude Sonnet 5.5 | Run on the current text. |
| Builder against plainly asking Claude for a skill | Not run | | Could be run; the builder has not been compared with it. |

Every other figure in this manual is from Claude Opus 5.5 only. Results can differ on another model.
The `--models` option runs the evals on others.

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

## The builder's own evals

The builder is held to the same evals it writes for other skills. The files are in `evals/`, and
anyone can re-run them with the commands below.

### Trigger evals

Claude Opus 5.5 in Claude Code, 2026-09-29. 16 prompts, 3 runs each, 48 runs, none invalid.

| | Runs | Correct |
|---|---|---|
| Should start (9 prompts: build a skill, audit one, run a skill's evals, "is it safe to install?") | 27 | **25** |
| Should stay quiet (7 prompts: CLAUDE.md, reviewing ordinary code, scanning package dependencies, …) | 21 | **21** |

Both misses are on one prompt, "Run the trigger evals for my changelog skill". The eval folder holds
no changelog skill, so in 2 of 3 runs the model searched for it, found none, and asked where it
was before loading any skill. The prompt names something that does not exist; it is a weakness of
that case rather than of the description.

### Quality evals, latest run

Claude Sonnet 5.5 in Claude Code, 2026-10-05, on the current text. Seven scenarios, 2 runs per
scenario and condition, graded blind by the same model against a rubric of 7 to 9 points.

| Scenario | With skill | Without skill |
|---|---|---|
| Eval cost warning before step 8, from pilot output already on disk | 15/16 | 8/8 |
| Audit a clean skill, no source material | 16/16 | 7/16 |
| Audit a downloaded skill with a planted credential stealer | 16/16 | 13/16 |
| Audit a skill that has no evals, and draft them | 14/14 | 8/14 |
| Audit a folder of three skills, one of them malicious | 18/18 | 14/18 |
| Build, with the opt-in Baseline offer after step 2 | 16/16 | 6/16 |
| Audit a skill that breaks the authoring rules | 15/16 | 8/16 |
| **All** | **110/112 (98 %)** | **64/104 (62 %)** |

- One run without the skill, in the cost-warning scenario, is left out: it stopped at a permission
  prompt for a file outside its folder. That column counts 8 points fewer for it.
- Both missed points with the skill are variance. Re-run 4 times, the authoring-rules scenario scored
  32/32. One cost-warning criterion (offering `--only` among the options) passed in 3 of 4 re-runs.
  In another re-run the model declined to quote the pilot figures, because the seeded eval files
  in that scenario are smaller than the pilot said; that is the skill working as written.
- Without the skill the model misses what the new scenarios test: the Baseline offer with its cost
  and default no, the Contents-list note, the Findings format and the one-at-a-time offer of fixes.
- The Baseline offer was also tried live, in a headless Build. "No" drafted nothing. "Yes" began
  drafting the quality scenarios but was refused write access to the skills folder, so it did not
  reach a Baseline run; try that path by hand.
- The `--models` option was exercised on Haiku and Sonnet. On Haiku the skill started, but the model
  still did not give the warning figures.

### Quality evals, earlier run

Claude Opus 5.5 in Claude Code. Five scenarios, 2 runs per scenario and condition, graded blind
against a rubric of 7 to 9 points.

| Scenario | With skill | Without skill |
|---|---|---|
| Eval cost warning before step 8, from pilot output already on disk | 15/16 | 15/16 |
| Audit a clean skill, no source material | 16/16 | 6/16 |
| Audit a downloaded skill with a planted credential stealer | 16/16 | 14/16 |
| Audit a skill that has no evals, and draft them | 14/14 | 3/7 |
| Audit a folder of three skills, one of them malicious | 18/18 | 12/18 |
| **All** | **79/80 (99 %)** | **50/73 (68 %)** |

One run without the skill ended with a grader reply that could not be read, so that column counts
7 fewer points. The runs without the skill for the clean, malicious and three-skill audits were
graded with a looser wording of the check-order criteria, one that also passed a run which only
said it ran a check; that favours the baseline, so the gap is if anything understated. The one point lost with the skill is grader strictness: the run stopped correctly
and asked which of the offered options to take, where the rubric wanted a plain go-ahead.

What the numbers say:

- **The cost warning gains nothing here.** With the pilot's output already in the folder, the model
  relays it well without the skill. The skill's contribution is running the pilot at all and
  stopping for the go-ahead, which this scenario does not isolate.
- **The model already spots obvious malware.** Without the skill it flagged the planted
  download-and-run line, the hidden Unicode character and the credential theft. What the skill adds
  is the procedure around it: the check order, blocking before any eval, and saying that a scan is
  best-effort.
- **The audit procedure is where the skill earns its keep.** Without it, the model did not group a
  multi-skill report by skill, did not exclude the malicious skill from evals, did not ask which
  skills to evaluate, and did not draft evals in a form it could run.

### How the evals are set up

- **Eval runs have no shell.** The runners block shell commands in every run, so a malicious skill
  under test can never execute anything. The builder's own scripts cannot run inside an eval either.
  The rubric therefore scores a run as correct when it runs a check, or says plainly that the check
  did not run and holds the evals. A run that claims a check it did not run fails.
- **The skill is loaded from where it is installed.** The runners test the copy in your skills
  folder, not the folder you pass on the command line. Install the version you mean to test first.
- **Run the two eval types one after the other**, not side by side. They share the five-hour window.

### What a full run costs

Measured on the runs above, in notional USD, which is what the same calls would cost on the API. On a
subscription they draw from your five-hour window instead.

| Run | Runs | Notional USD | Share of the five-hour window |
|---|---|---|---|
| Trigger evals | 48 | about $5.30 | about 30 % |
| Quality evals, with and without the skill (7 scenarios) | 28 plus 28 grades | about $6.20 | about 25 % |

The pilot measures this before every run; these figures are only a guide. They are for one model: each
extra model in `--models` repeats the whole plan, and the Eval cost warning multiplies by the count.

```text
python <skills folder>/grounded-skill-builder/scripts/run_trigger_evals.py <skills folder>/grounded-skill-builder --pilot --out <run folder>
python <skills folder>/grounded-skill-builder/scripts/run_quality_evals.py <skills folder>/grounded-skill-builder --pilot --out <run folder>
```

Add `--models <model>[,<model>...]` to either runner to test on other models than the one in use (an
alias or a full model name, e.g. haiku, sonnet). Without it, no model is passed to `claude`.

Drop `--pilot` and keep the same `--out` to run the full plan; the pilot's runs are reused.

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The steps the agent follows. |
| `references/grounding-rules.md` | The rules behind each step, with sources, the formats of both eval files, and what to look for per model. |
| `references/audit.md` | The procedure for auditing an existing skill. |
| `references/authoring-rules.md` | The authoring rules a Build or Audit checks a skill against, split into `fix` and `note`. |
| `scripts/extract_user_turns.py` | Prints only what the user typed in Claude Code transcripts. |
| `scripts/evalcheck.py` | Checks eval files before any paid run and says which case or scenario is wrong and how to fix it: `python scripts/evalcheck.py <eval file>`. |
| `scripts/run_trigger_evals.py` | Runs the trigger evals and reports which prompts started the skill. |
| `scripts/run_quality_evals.py` | Runs the quality evals with and without the skill and grades each run blind. |
| `scripts/security_scan.py` | Scans a skill folder, or each skill in a folder of skills, and prints its security findings as JSON. |
| `scripts/make_dist.py` | Zips a finished skill; refuses while any file names a path or the user of this machine. `--check` runs only that check. |
| `scripts/evalkit.py` | Shared code for the two eval runners: runs `claude`, reads its output, and estimates and totals the cost. |
| `scripts/test_scripts.py` | Checks the shared eval code, the eval-file checker and the security scan: `python scripts/test_scripts.py`. |
| `evals/trigger-evals.json` | Trigger evals for this builder itself. |
| `evals/quality-evals.json` | Quality evals for this builder itself. |
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

Build and Audit also check a skill against the rules in Anthropic's
[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
which the specification's validator does not. Each broken rule is a `fix` (it breaks discovery,
portability or loading: a description not in the third person, a reserved word or an XML tag in the
name, backslash paths, references nested more than one level, scripts that need a CLI or network
without a `compatibility` line) or a `note` (advice: a missing Contents list, vague or inconsistent
names, a menu instead of a default, undocumented constants in scripts, and similar). The validator
passes a name that contains "claude" and a description that contains an XML tag, so the builder
checks those two by hand.

The eval runners call the `claude` command-line tool, so the full build process needs Claude Code;
the frontmatter says so with `compatibility: Claude Code only`. That field has been checked only
with the specification's validator. Uploading the skill to claude.ai or to the API was not tested,
so whether those hosts accept the `compatibility` field is unconfirmed.

The two downloads are pinned, and a bump is deliberate: change the pin, re-run the script tests and
the validator, and only then keep it.

---

## Built with

**Nothing has to be downloaded beyond Claude Code and Python.** The scripts use only the Python
standard library.

| Component | What the tool uses it for | Where it comes from | License |
|---|---|---|---|
| [Claude Code](https://www.anthropic.com/claude-code) | Runs the builder; its command-line tool runs the eval prompts and the grader | Anthropic; needs a Claude subscription or API account | **Commercial** |
| [Python 3](https://www.python.org/) | Runs the scripts | python.org, or your system's package manager | [PSF License](https://docs.python.org/3/license.html), free |
| Python standard library: `argparse`, `json`, `subprocess`, `concurrent.futures`, `hashlib`, `os`, `re`, `tempfile`, `zipfile`, `getpass`, `datetime`, `sys` | Command-line options, reading transcripts and eval files, calling `claude`, running evals in parallel, hashing seeded files, building the zip, showing the usage window's reset in local time | Ships with Python | PSF License, free |
| Optional: the `writing-for-agents` skill | Tightens the wording of the skill being built | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT, free |
| Optional: [uv](https://docs.astral.sh/uv/) | Runs skills-ref and the Cisco skill-scanner without installing them | Its site, or your package manager | MIT or Apache-2.0, free |
| Optional: [Cisco skill-scanner](https://pypi.org/project/cisco-ai-skill-scanner/) ([repository](https://github.com/cisco-ai-defense/skill-scanner)) | Static security scan of each skill it builds or audits, before its evals run | Downloaded on demand by `uvx`, pinned to one version, and cached | Apache-2.0, free |
| Optional: [skills-ref](https://github.com/agentskills/agentskills) | Validates each skill it builds or audits against the Agent Skills specification | Installed, or fetched by `uvx` at a pinned commit | Apache-2.0, free |

Claude Code is the only commercial component. Without the optional skill the builder says so and
skips that step. Without uv it checks the specification's rules by hand, and the security scan runs only its own
search for payload shapes; the builder then tells you so and waits for your go-ahead before the evals.

---

## Credits

- **Sources of the rules.** The rules in `references/grounding-rules.md` are distilled, in our own
  words, from two public talks, one guidance page and two security sources. No transcript text is
  included.
  - IBM Technology, [*5 Best Practices for Building AI Agent Skills*](https://www.youtube.com/watch?v=qYNs80FKIVc) (YouTube)
  - Philipp Schmid (Google DeepMind), [*Don't Ship Skills Without Evals*](https://www.youtube.com/watch?v=0vphxNt4wyk), AI Engineer (YouTube)
  - Anthropic, [*Skill authoring best practices*](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), the source of the authoring rules in `references/authoring-rules.md`
  - Snyk, [*ToxicSkills*](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/), a study of malicious agent skills
  - Cisco AI Defense, [skill-scanner](https://github.com/cisco-ai-defense/skill-scanner), which the security scan runs
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

**The prose**, meaning `SKILL.md`, the reference files, the eval files and this manual, is licensed
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see [`LICENSE-docs`](LICENSE-docs)).
You may share and adapt it for any purpose if you give credit.

*This summary is not a license. The linked texts are the actual terms.*

---

## Version history

Newest first.

### 1.2.0 (2026-10-05)

- Build and Audit check a skill against Anthropic's authoring rules and report each as a `fix` or a `note`.
- A Build can offer a **Baseline** pass after the source material is mined: the quality scenarios run
  without the skill first. The default is no.
- Both eval runners take `--models` to test on other models than the one in use; the cost warning
  multiplies by the number of models.
- Eval files are checked before any paid run. The Cisco skill-scanner and `skills-ref` downloads are
  pinned. The skill declares `compatibility: Claude Code only`.

### 1.1.1 (2026-10-04)

- Web search and web fetch are blocked in every quality eval run, so a run without the skill
  cannot stall at a permission prompt for them.

### 1.1.0 (2026-09-29)

- Audit an existing skill, or a folder of skills, with the same checks as a Build.
- Security scan before the evals run.
- Eval cost warning: a pilot measures the cost and the five-hour usage window before every eval run.

### Before 1.1.0 (2026-09-27 to 2026-09-28)

- First release: builds a skill from supplied source material, runs trigger and quality evals with
  and without the skill, checks the skill against the Agent Skills specification, writes a README,
  and zips the result for sharing.
