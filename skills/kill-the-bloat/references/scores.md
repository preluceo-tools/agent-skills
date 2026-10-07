# Generic usefulness scores

Researched 2026-10-07. Scores are a synthesis for a typical Claude Code user, not a published metric and not the current user's preference. Confidence says how well the item's function is documented, not how right the score is. Items marked `low` are reasoned estimates with no source; say so when presenting them.

## Contents

- Tools
- Settings flags
- Bundled and common skills
- Ecosystem items
- Settings semantics

Source keys:
- DOC-TOOLS https://code.claude.com/docs/en/tools-reference
- DOC-SKILLS https://code.claude.com/docs/en/skills
- DOC-SET https://code.claude.com/docs/en/settings-reference
- DOC-MCP https://code.claude.com/docs/en/mcp
- DOC-PERM https://code.claude.com/docs/en/permissions
- DOC-WF https://code.claude.com/docs/en/workflows
- DOC-ART https://code.claude.com/docs/en/artifacts
- DOC-COST https://code.claude.com/docs/en/costs
- DOC-SUB https://code.claude.com/docs/en/sub-agents
- POC https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt (one author's own list and token measurements)
- PLAN https://claudelog.com/mechanics/plan-mode , https://blog.openreplay.com/plan-mode-claude-code-complex-tasks/
- SKL-REV https://batsov.com/articles/2026/03/11/essential-claude-code-skills-and-commands/ , https://www.wearedevelopers.com/magazine/740-9-claude-code-skills-to-speed-up-your-workflow

## Tools (disable with a bare name in `permissions.deny`)

| name | what it does | score | daily use | tokens | conf | sources |
|---|---|---|---|---|---|---|
| Workflow | Runs a script that orchestrates many subagents in the background | 3 | rare | ~5307 (POC) | med | DOC-TOOLS, POC |
| DesignSync | Design-sync tool, not in the official tools list | 1 | rare | ~2245 (POC) | low | POC only |
| Monitor | Streams a background command's output lines to Claude | 5 | occasional | ~1942 (POC) | med | DOC-TOOLS |
| CronCreate | Schedules a recurring or one-shot prompt in the session | 3 | rare | n/a | med | DOC-TOOLS |
| CronDelete | Cancels a scheduled task | 2 | rare | n/a | med | DOC-TOOLS |
| CronList | Lists scheduled tasks | 2 | rare | n/a | med | DOC-TOOLS |
| ScheduleWakeup | Lets Claude pace a self-timed `/loop` | 3 | rare | n/a | med | DOC-TOOLS |
| SendMessage | Messages or continues another agent | 4 | occasional | n/a | low | reasoned; matters only if you use subagents |
| PushNotification | Desktop and, with Remote Control, phone notifications | 3 | rare | n/a | med | DOC-TOOLS |
| RemoteTrigger | Creates and runs Routines on claude.ai, backs `/schedule` | 2 | rare | n/a | med | DOC-TOOLS |
| EnterPlanMode | Lets the model start plan mode itself; you can still use Shift+Tab or `/plan` | 6 | occasional | n/a | med | DOC-TOOLS, PLAN |
| ExitPlanMode | Presents the plan for approval; plan mode likely breaks without it | 8 | occasional | n/a | med | DOC-TOOLS. Disagrees with POC; breakage unverified |
| EnterWorktree | Creates or enters an isolated git worktree | 5 | occasional | n/a | med | DOC-TOOLS. Keep if you run background or parallel jobs |
| ExitWorktree | Leaves the worktree | 5 | occasional | n/a | med | DOC-TOOLS |
| NotebookEdit | Edits Jupyter notebook cells | 3 (8 for notebook users) | rare | n/a | high | DOC-TOOLS |
| TaskStop | Stops a running background task | 5 | occasional | n/a | low | reasoned |
| WebFetch | Fetches a URL | 8 | daily | n/a | high | DOC-TOOLS |
| WebSearch | Web search | 8 | daily | n/a | high | DOC-TOOLS |
| ReportFindings | Renders code-review findings as a list | 3 | rare | n/a | med | DOC-TOOLS |
| ShareOnboardingGuide | Uploads ONBOARDING.md for `/team-onboarding` | 1 | rare | n/a | high | DOC-TOOLS |
| EndConversation | Ends the session on sustained abuse | 1 | rare | n/a | high | DOC-TOOLS |
| ListAgents | Lists subagents | 3 | rare | n/a | low | reasoned |
| ToolSearch | Loads deferred tools and MCP tools on demand; protected | 9 | daily | n/a | high | DOC-TOOLS, DOC-MCP |
| Artifact | Publishes a page as a private claude.ai artifact; needs claude.ai login | 4 | occasional | n/a | med | DOC-TOOLS, DOC-ART |
| ArtifactComments | Reads and answers artifact comments | 2 | rare | n/a | low | reasoned |
| ArtifactData | Reads and writes an artifact's shared database | 2 | rare | n/a | low | reasoned |
| mcp__ide__executeCode | Runs code in the IDE's Jupyter kernel | 2 | rare | n/a | low | reasoned |
| mcp__ide__getDiagnostics | Returns IDE errors and warnings | 5 | occasional | n/a | low | reasoned; needs IDE integration |

## Settings flags

| key | what it does | score | daily use | conf | sources |
|---|---|---|---|---|---|
| disableWorkflows | Removes the Workflow tool, bundled workflow commands, `/workflow-authoring`, the `ultracode` keyword. Env alternative `CLAUDE_CODE_DISABLE_WORKFLOWS=1` | 3 | rare | med | DOC-WF, DOC-SET, POC |
| disableRemoteControl | Turns off Remote Control (drive a local session from phone or browser) | 3 | rare | med-low | DOC-SET |
| disableClaudeAiConnectors | Stops fetching MCP connectors configured in your claude.ai account. Single connector: `deniedMcpServers`. `true` from any scope wins | 4 as a feature (flag worth 8 if you use no connectors) | rare | high | DOC-MCP, DOC-SET |
| enableArtifact | Set `false` to remove the Artifact tool. Replaces the deprecated `disableArtifact`, which still works | 4 | occasional | high | DOC-ART, DOC-SET |
| disableBundledSkills | Removes the bundled skills and bundled workflows, all or nothing. Per-skill: `skillOverrides`. | 5 | occasional | med | DOC-SKILLS, DOC-SET, POC |

## Bundled and common skills (disable with `skillOverrides`)

`skillOverrides` values: `on`, `name-only`, `user-invocable-only` (hidden from Claude, still in the `/` menu), `off` (hidden everywhere). Each enabled skill's name and description is sent on every turn, description plus `when_to_use` cut at 1,536 characters (DOC-SKILLS).

| name | what it does | score | daily use | conf | sources |
|---|---|---|---|---|---|
| simplify | Reviews changed code for reuse and simplification, applies fixes | 8 | daily | high | SKL-REV |
| code-review (review) | Reviews a diff or PR for bugs | 8 | occasional | high | SKL-REV, DOC-SKILLS |
| skill-creator | Creates, packages and evals skills | 7 | rare, high value | med | SKL-REV |
| init | Generates a CLAUDE.md | 6 | once per repo | med | POC names it removable |
| security-review | Security review of pending changes | 6 | occasional | med | SKL-REV |
| loop | Runs a prompt on an interval | 6 | occasional | med | DOC-SKILLS, SKL-REV |
| run | Launches and drives the project's app | 6 | occasional | med | DOC-SKILLS |
| update-config | Edits settings.json | 6 | rare | low | reasoned |
| claude-api | Claude API and SDK reference | 5 (9 if you build on Claude) | rare | med | DOC-SKILLS, SKL-REV |
| fewer-permission-prompts | Proposes a read-only allowlist | 5 | rare | low | reasoned |
| claude-in-chrome | Browser automation through the Chrome extension | 5 | occasional with extension | low | reasoned |
| pptx, docx, xlsx, pdf | Office and PDF file work | 5 | rare | low | reasoned; check `/skills`, these may come from a plugin |
| schedule | Cloud scheduled agents | 4 | rare | low | reasoned |
| deep-research | Multi-source research report | 4 | rare | low | reasoned |
| dataviz | Chart design guidance | 3 | rare | low | POC names it |
| artifact-design | Artifact page contract | 3 | rare | low | reasoned |
| keybindings-help | Edits keybindings.json | 2 | rare | low | reasoned |
| plugin-authoring | Writes hook-module plugins | 2 | rare | low | reasoned |
| workflow-authoring | Reference for Workflow scripts; goes away with `disableWorkflows` | 2 | rare | med | DOC-SKILLS |
| artifact-diagramming, artifact-capabilities | Artifact helpers | 2 | rare | low | reasoned |
| import-memory | One-time memory import | 1 | rare | low | reasoned |

## Ecosystem items

| name | what it does | score | conf | sources |
|---|---|---|---|---|
| MCP servers you use | External tools; with tool search only names enter context until used. 5 servers cost ~55k tokens before tool search and ~8.7k after (Anthropic) | 8 used, 2 idle | high | DOC-MCP, DOC-COST, https://www.anthropic.com/engineering/advanced-tool-use |
| claude.ai connectors (Notion, Asana, Atlassian, Figma, HubSpot, Linear, Microsoft 365, Canva, Box, Intercom, ...) | Account-level MCP servers, auto-listed when logged in with a claude.ai subscription. Unauthenticated ones show only authenticate stubs | 2 unused, 7 used | med | DOC-MCP |
| Plugins | Each enabled plugin adds skill and agent descriptions every turn; cost grows with the number of plugins | 6, varies | high | DOC-SKILLS, DOC-COST |
| Subagent types | Agent tool lists types. Built-ins Explore and general-purpose protect main context. Remove one with `Agent(Name)` in deny | 7 built-ins, 3 niche plugin agents | high | DOC-SUB |

## Settings semantics (verified in the docs)

- A bare tool name in `permissions.deny` removes the tool from Claude's context (DOC-PERM). That a scoped rule like `Bash(rm *)` keeps the definition is implied by the contrast and stated only by POC.
- Scopes, highest first: managed, `--settings`, `.claude/settings.local.json`, `.claude/settings.json`, user `~/.claude/settings.json`. `disableClaudeAiConnectors: true` from any scope wins.
- Claude.ai connectors and Artifact exist only with a claude.ai login; API key, Bedrock and Vertex users already have neither.
