# Grounding rules

The rules each step of `SKILL.md` enforces, distilled from the sources below. Tags mark each rule's source. The checklist of authoring rules for step 4 and Audit is in [authoring-rules.md](authoring-rules.md).

## Contents

- Source material over generation
- The description is the trigger
- Lean body, disclosed detail
- Freedom matched to fragility
- Vet what runs
- Capability vs preference
- No-ops
- Evals, with the trigger and quality eval formats
- Reading results per model

- **[S1]** IBM Technology, *5 Best Practices for Building AI Agent Skills* (YouTube) — https://www.youtube.com/watch?v=qYNs80FKIVc
- **[S2]** Philipp Schmid (Google DeepMind), *Don't Ship Skills Without Evals*, AI Engineer (YouTube) — https://www.youtube.com/watch?v=0vphxNt4wyk
- **[S3]** Building and evaluating the `to-checklist` skill with this builder (2026-09-28): what running the evals for real turned up.
- **[S4]** Snyk, *ToxicSkills* study of agent skills supply chain compromise — https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
- **[S5]** Cisco AI Defense, *skill-scanner* — https://github.com/cisco-ai-defense/skill-scanner
- **[S6]** The design session that added the security scan to this builder (2026-09-28): which scanners were weighed and what the scan must do when it cannot run.
- **[S7]** Anthropic, *Skill authoring best practices* — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

## Source material over generation

Generated-from-nothing skills restate what the model already knows and measurably underperform human-written ones. The content must be something the model cannot produce on its own: a hand-run of the task with its corrections written down, or existing artifacts — runbooks, reports, review comments. [S1] [S2]

Gotchas are the highest-value section of a body: each hand correction of the agent is one, and an unrecorded one gets repeated next week. [S1]

## The description is the trigger

At startup the agent sees only name and description, so they alone decide whether the skill ever runs. State what it does, when to use it, and why; write directives, not essays, in the third person (the description is injected into the system prompt). [S1] [S2] [S7]

Models under-trigger, so lean slightly pushy. [S1] [S2]

Scope the negative side too: a broad description ("web development") over-triggers on neighbouring work. Name what it is *not* for. [S2]

The description is paid on every model call — keep it short. Limits: name 64 characters, description 1024. [S1] [S2] [S7]

## Lean body, disclosed detail

The body loads whole once the skill fires. Write only what the model wouldn't know; stay under roughly 500 lines. Branch-specific detail (e.g. one file per cloud provider) lives in `references/`, opened only when needed, linked straight from the body, and given a Contents list when over 100 lines. [S1] [S2] [S7]

## Freedom matched to fragility

Loose steps get goals and constraints, not step-by-step lists. Steps that must be identical every run get a script in `scripts/` — scripts aren't loaded into context and don't guess. Say explicitly whether a file is to be *run* or *read*. A fixed, always-identical workflow may not need a skill at all — just a script. [S1] [S2] [S7]

## Vet what runs

A skill folder can execute code with access to the filesystem, network, and credentials; treat it like any dependency and state what each script reaches. [S1]

Skill registries carry real malware: a scan of about 4,000 public skills found prompt injection in 36% and 76 confirmed malicious payloads, built for credential theft, backdoors and data exfiltration. Every confirmed malicious skill paired code with injected instructions, and the most typical payload sits in the SKILL.md prose, not in a script. Scan the whole folder, prose included. [S4]

Scan before the evals: the eval runs load the skill and can run its scripts. [S6]

- A static scanner catches known patterns without an account or an upload. The Cisco skill-scanner's default analyzers are static (YAML/YARA signatures, pipeline taint); its LLM, VirusTotal and cloud analyzers need API keys and send content away, so they stay off. Stop at high severity. [S5] [S6]
- A plain search adds the payload shapes that need no scanner: invisible or bidirectional Unicode, long base64 blobs, download-and-run pipes (a fetched script piped into a shell or interpreter), network hosts, credential environment variables and credential files. [S4] [S6]
- Neither checks intent, so a fresh read-only subagent compares each script with what the Scripts section declares; an undeclared reach blocks. [S6]
- A scanner that cannot run (no `uv`, no network, a certificate error) is not a pass: say so, give the cause and the fix, and hold the evals for the user's go-ahead. [S6]
- A clean scan is best-effort, not proof; payloads split across several skills are out of its reach. [S6]

## Capability vs preference

Capability skills teach what the model can't yet do and should be retired once it can. Preference skills encode a team's own way and are durable. Evals tell you which state a skill is in. [S2]

## No-ops

AI-written skills collect instructions that change nothing ("write clean code"). Each costs tokens on every load; strip them. [S1] [S2]

## Evals

Every skill ships with evals. Start small: 5 prompts that should trigger, 5 that should not; add real production traces when you have them. [S2] [S7]

Grade outcomes, isolate runs, several trials per case, and run with and without the skill (ablation) to know when to retire it. [S2]

Run them after the last text edit — writing-for-agents and the no-op strip change the words that trigger and steer the skill — and again after every fix. [S3]

Trigger evals only show that the skill fires, and an absent skill cannot fire, so they carry no ablation. The ablation needs quality evals: the same scenario with and without the skill, graded blind against a rubric. In the `to-checklist` build, trigger evals passed 30/30 while quality evals found a real defect (the agent wrote a field in a shape the bundled template did not read, leaving a page section empty). [S3]

What made the runs trustworthy [S3]:

- Count a trigger only from a Skill tool call naming the skill. Matching the skill's name anywhere in the output gave a false positive when the run folder's path contained it.
- Mark runs that end in an API error (usage limit, HTTP 429) as invalid; scored as zero they look like a broken skill.
- Mark runs that stop at a permission prompt as invalid too. On Windows a temp folder can come back as a short 8.3 path (`ABCDEF~1`); Claude Code treats that as suspicious and blocks every file access, and the grader then scores an empty run. Expand run folders to their full path. A headless run may also be refused the skill's own `references/` and `assets/`, which lie outside its folder; pass the skill folder with `--add-dir` in the with-skill condition.
- Isolate each run in its own folder with seeded files, and hash the seeded files so the grader sees unwanted edits.
- Give skills that wait for the user their answer inside the prompt, or the headless run stops at the question.
- `--disable-slash-commands` removes all skills for the baseline, not only the one under test; say so when reporting.

### Reading results per model

A skill is tested on the models it targets (`--models`); the same text can pass on one and fail on another. When reading a failed criterion, ask the question for that model:

- **Haiku**: is there enough guidance? Failures here usually mean a step or an example is missing.
- **Sonnet**: is it clear and efficient? Failures here usually mean ambiguity, or steps that cost more than they change.
- **Opus**: is it over-explained? A with-skill score no better than without often means the text restates what the model already does.

### Trigger eval format

`evals/trigger-evals.json`:

```json
{
  "skill": "<skill name>",
  "cases": [
    {
      "id": "happy-1",
      "prompt": "<what a user would actually type>",
      "should_trigger": true,
      "expected": ["<observable outcome that shows success>"]
    },
    {
      "id": "negative-1",
      "prompt": "<a near-miss task sharing vocabulary>",
      "should_trigger": false,
      "expected": []
    }
  ]
}
```

`expected` holds outcome checks a regex or a rubric can grade; empty is fine for negatives.

### Quality eval format

`evals/quality-evals.json`:

```json
{
  "skill": "<skill name>",
  "scenarios": [
    {
      "id": "<branch name>",
      "files": { "<relative path>": "<file content seeded before the run>" },
      "prompt": "<what a user would type, plus the answers to any question the skill asks>",
      "rubric": ["<criterion a grader can check from the files and the final message>"]
    }
  ]
}
```
