<div align="center">

# agent-skills

### Agent skills for Claude Code, each one built from real work and measured with evals.

<img src="https://img.shields.io/badge/Claude%20Code-skills-b1b9f9?style=flat-square&labelColor=0d1117" alt="Claude Code skills" />
<img src="https://img.shields.io/badge/Agent%20Skills-spec%20valid-b1b9f9?style=flat-square&labelColor=0d1117" alt="Valid against the Agent Skills specification" />
<img src="https://img.shields.io/badge/license-GPL%20v3%20%C2%B7%200BSD%20%C2%B7%20CC%20BY%204.0-b1b9f9?style=flat-square&labelColor=0d1117" alt="GPL v3, 0BSD and CC BY 4.0" />

</div>

This is a collection of agent skills. Each skill is a folder under `skills/` with its own manual,
evals and license files, so you can take any one of them on its own.

> [!NOTE]
> **Unofficial.** This project is not affiliated with, endorsed by, or supported by Anthropic.
> Claude and Claude Code are named here only to say which tool these skills run in.

---

## Skills

| Skill | What it does |
|---|---|
| [grounded-skill-builder](skills/grounded-skill-builder/) | Builds a new skill from source material you supply (a transcript, a runbook, review comments), then runs its evals with and without the skill. Also audits an existing skill, yours or a downloaded one: spec, security scan, rules and evals. |
| [to-checklist](skills/to-checklist/) | Turns what you have to verify or do by hand into an offline HTML checklist, and reads your results back. |
| [atmega-baremetal](skills/atmega-baremetal/) | Writes register-level C firmware for ATmega chips (ATmega328P, 2560, 4809 and others) with avr-gcc, no Arduino framework: a portable Makefile, 26 compile-checked examples, and Wokwi simulator files for the chips a simulator can run. |

Test tooling that is not part of a skill lives in `tools/` (for now the Node.js gates for
**atmega-baremetal**).

Each skill's `README.md` covers what it does, how to use it, what it depends on, and which other
skills it calls.

---

## Install

Copy the skill's folder from `skills/` into your personal skills folder:

```text
~/.claude/skills/<skill name>/
```

On Windows that is `%USERPROFILE%\.claude\skills\<skill name>\`. To limit a skill to one project, put
it in `<project>/.claude/skills/<skill name>/` instead.

---

## Other agents

The skills are plain `SKILL.md` folders in the open Agent Skills format, so any harness that loads
that format (e.g. Codex, Antigravity) can in principle use them. Copy the folder to wherever that
harness looks for skills.

- **to-checklist** has no Claude-specific parts. It writes an HTML page and reads back plain text.
- **atmega-baremetal** has no Claude-specific parts in the skill itself. Only its model-graded evals call the
  `claude` command-line tool; its deterministic gates need Node.js and avr-gcc.
- **grounded-skill-builder** has Claude-specific parts: its eval runners call the `claude`
  command-line tool, its transcript extractor reads Claude Code session files, and its steps name
  Claude Code's Skill and Agent tools. Elsewhere, the build steps still read as instructions, but
  the eval scripts need adapting.

> [!IMPORTANT]
> **Tested only with Claude Code.** No other harness has been tried.

---

## Agent Skills standard

Every skill here follows the open [Agent Skills specification](https://agentskills.io/specification)
and passes its validator:

```text
skills-ref validate skills/<skill name>
```

---

## Disclaimer

These skills are provided **"as is", without warranty of any kind**, express or implied, including
but not limited to the warranties of merchantability, fitness for a particular purpose and
non-infringement. You use them entirely at your own risk. Each skill's manual says what it touches.

## License

© 2026 preluceo

**The code**, meaning scripts and templates, is licensed under the
[GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html) (see [`LICENSE`](LICENSE)).
**The prose**, meaning each `SKILL.md`, reference file, eval file and manual, is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see [`LICENSE-docs`](LICENSE-docs)).
Each skill's manual says which of its files fall under which. The exception is
**atmega-baremetal**, whose code (examples and templates) is under the
[BSD Zero Clause License](https://opensource.org/license/0bsd) instead, so firmware generated from it
carries no obligation; see its own `LICENSE`.

*This summary is not a license. The linked texts are the actual terms.*
