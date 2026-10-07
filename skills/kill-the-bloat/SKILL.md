---
name: kill-the-bloat
description: Interactive Q&A that trims Claude Code's per-request payload. It inventories the installed tools, skills, plugins, MCP servers and connectors, shows each with a 0-10 generic usefulness score, asks Keep or Disable, then writes the disable flags, deny rules and skillOverrides into settings.json so no hand-editing is needed. Use when the user wants to cut token bloat, disable unused Claude Code tools, skills or connectors, clean up the system prompt, or shrink /context. Not for editing hooks or permissions allow-lists (use update-config), nor for CLAUDE.md compression.
compatibility: Requires Python 3 to run scripts/apply_settings.py.
---

# Kill the bloat

Result: the user's `settings.json` carries the disable entries they accepted, written by script, after a Keep/Disable Q&A.

## 1. Pick scope and measure

Ask which file to write: user `~/.claude/settings.json` (all projects) or project `<repo>/.claude/settings.json`. Ask every run. Read the chosen file if it exists.

Ask the user to run `/context` and paste the total, to compare at the end.

## 2. Inventory

List, from your own tool list, skills list and MCP servers in this session: deferred and built-in tools, skills, plugin skills, MCP and connector servers. The settings file shows only what is already disabled: skip those items.

Read [references/scores.md](references/scores.md) for the score, description and daily-use note of each item. Items missing from it: web-search them, mark them `unscored, web` and say what the source was. On a refresh request, re-search the file's `low` rows first and update it.

Never offer these: `Bash, Read, Edit, Write, Grep, Glob, Skill, ToolSearch, Agent, AskUserQuestion`. The script refuses them. Say once that they are skipped.

## 3. Ask

Group items into the cheapest switch that covers them: a `disable*` flag for a whole feature, a bare `permissions.deny` name for one tool, `skillOverrides` for one skill. Offer a flag before its individual members.

Ask with AskUserQuestion, 4 items per call, each as: name, one-line purpose, `score N/10`, daily-use note, and the token figure when scores.md has one. Options: Keep (Recommended when score ≥ 6), Disable (Recommended when score ≤ 3), and for skills also `user-invocable-only`. This is generic research, not the user's preference: say so once.

Warn in the question when an item has a known dependency:
- ExitPlanMode and EnterPlanMode go together; denying ExitPlanMode likely breaks plan mode.
- EnterWorktree, ExitWorktree, TaskStop, SendMessage matter for background or multi-agent runs.
- `disableWorkflows` also removes `workflow-authoring` and the `ultracode` keyword.
- `disableBundledSkills` also removes bundled workflows; slash commands staying typable is confirmed in the docs only for `/doctor`.
- `disableClaudeAiConnectors` and Artifact only matter with a claude.ai login.

## 4. Write

Write the plan to `plan.json` in the working directory, e.g. `{"deny": ["CronCreate", "CronDelete"], "flags": {"disableWorkflows": true}, "skillOverrides": {"dataviz": "off"}}`. Rules: bare tool names only (a scoped rule like `Bash(rm *)` keeps the definition and saves nothing); turn artifacts off with `"enableArtifact": false`, not the deprecated `disableArtifact`.

*Run* `scripts/apply_settings.py <settings.json> plan.json` and show the diff. Ask for confirmation. On yes, *run* it again with `--write`; it writes `<file>.bak` first and merges into existing keys. Only the script writes the settings file. If the session has no shell, tell the user to run the script themselves, and stop.

## 5. Verify

Tell the user to restart Claude Code, run `/context`, and compare with the first number. To undo, copy the `.bak` back.

## Gotchas

- Higher scopes win for flags, `deny` lists combine across files: a user-level deny still applies in every project.
- Two files in one scope, `settings.json` and `settings.local.json`, are separate.
- Many tools are deferred behind ToolSearch, so real savings can be smaller than the figures in scores.md.

## Scripts

- `scripts/test_apply_settings.py` runs `apply_settings.py` on seeded files in a temp folder it deletes; the temp location comes from the TMPDIR, TEMP or TMP variable. No network, no credentials.
- `scripts/apply_settings.py` reads a settings file and a plan file, writes the settings file (creating missing parent folders) and a `.bak` copy next to it, only with `--write`. No network, no credentials.
