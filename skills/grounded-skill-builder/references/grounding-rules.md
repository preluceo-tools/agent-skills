# Grounding rules

The rules each step of `SKILL.md` enforces, distilled from two talks. Tags mark each rule's source.

- **[S1]** IBM Technology, *5 Best Practices for Building AI Agent Skills* (YouTube) — https://www.youtube.com/watch?v=qYNs80FKIVc
- **[S2]** Philipp Schmid (Google DeepMind), *Don't Ship Skills Without Evals*, AI Engineer (YouTube) — https://www.youtube.com/watch?v=0vphxNt4wyk
- **[S3]** Building and evaluating the `to-checklist` skill with this builder (2026-09-28): what running the evals for real turned up.

## Source material over generation

Generated-from-nothing skills restate what the model already knows and measurably underperform human-written ones. The content must be something the model cannot produce on its own: a hand-run of the task with its corrections written down, or existing artifacts — runbooks, reports, review comments. [S1] [S2]

Gotchas are the highest-value section of a body: each hand correction of the agent is one, and an unrecorded one gets repeated next week. [S1]

## The description is the trigger

At startup the agent sees only name and description, so they alone decide whether the skill ever runs. State what it does, when to use it, and why; write directives, not essays. Models under-trigger, so lean slightly pushy. [S1] [S2]

Scope the negative side too: a broad description ("web development") over-triggers on neighbouring work. Name what it is *not* for. [S2]

The description is paid on every model call — keep it short. Limits: name 64 characters, description 1024. [S1] [S2]

## Lean body, disclosed detail

The body loads whole once the skill fires. Write only what the model wouldn't know; stay under roughly 500 lines. Branch-specific detail (e.g. one file per cloud provider) lives in `references/`, opened only when needed. [S1] [S2]

## Freedom matched to fragility

Loose steps get goals and constraints, not step-by-step lists. Steps that must be identical every run get a script in `scripts/` — scripts aren't loaded into context and don't guess. Say explicitly whether a file is to be *run* or *read*. A fixed, always-identical workflow may not need a skill at all — just a script. [S1] [S2]

## Vet what runs

A skill folder can execute code with access to the filesystem, network, and credentials; treat it like any dependency and state what each script reaches. [S1]

## Capability vs preference

Capability skills teach what the model can't yet do and should be retired once it can. Preference skills encode a team's own way and are durable. Evals tell you which state a skill is in. [S2]

## No-ops

AI-written skills collect instructions that change nothing ("write clean code"). Each costs tokens on every load; strip them. [S1] [S2]

## Evals

Every skill ships with evals. Start small: 5 prompts that should trigger, 5 that should not; add real production traces when you have them. [S2]

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
