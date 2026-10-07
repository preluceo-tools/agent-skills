#!/usr/bin/env python3
"""Merge a kill-the-bloat plan into a Claude Code settings.json, with diff and backup.

usage: apply_settings.py <settings.json> <plan.json> [--write]

plan.json: {"deny": ["Tool", ...], "flags": {"disableWorkflows": true, ...},
            "skillOverrides": {"skill": "off" | "user-invocable-only"}}
Without --write: print the diff only. With --write: copy to <file>.bak, then write.
"""
import difflib, json, shutil, sys
from pathlib import Path

# Core tools and the Q&A tool itself: never written to deny, whatever the plan says.
PROTECTED = {"Bash", "Read", "Edit", "Write", "Grep", "Glob", "Skill", "ToolSearch", "Agent", "AskUserQuestion"}
# Settings keys the skill may set; anything else is refused so a typo never lands in settings.json.
FLAGS = {"disableBundledSkills", "disableWorkflows", "disableRemoteControl", "disableClaudeAiConnectors", "disableArtifact", "enableArtifact"}
# The four skillOverrides values Claude Code accepts.
MODES = {"on", "name-only", "user-invocable-only", "off"}


def merge(cur, plan):
    bad = [t for t in plan.get("deny", []) if t in PROTECTED]
    if bad:
        raise SystemExit(f"refused, protected tools in deny: {bad}")
    for t in plan.get("deny", []):
        if "(" in t:
            raise SystemExit(f"refused, scoped rule keeps the tool definition, use a bare name: {t}")
    unk = set(plan.get("flags", {})) - FLAGS
    if unk:
        raise SystemExit(f"refused, unknown flags: {sorted(unk)}")
    for s, m in plan.get("skillOverrides", {}).items():
        if m not in MODES:
            raise SystemExit(f"refused, skillOverrides[{s}] must be one of {sorted(MODES)}")
    out = json.loads(json.dumps(cur))
    deny = out.setdefault("permissions", {}).setdefault("deny", [])
    deny += [t for t in plan.get("deny", []) if t not in deny]
    out.update(plan.get("flags", {}))
    out.setdefault("skillOverrides", {}).update(plan.get("skillOverrides", {}))
    if not out["skillOverrides"]:
        del out["skillOverrides"]
    return out


def main():
    args = [a for a in sys.argv[1:] if a != "--write"]
    if len(args) != 2:
        raise SystemExit(__doc__)
    path, plan = Path(args[0]), json.loads(Path(args[1]).read_text(encoding="utf-8"))
    old = path.read_text(encoding="utf-8") if path.exists() else "{}"
    new = json.dumps(merge(json.loads(old), plan), indent=2, ensure_ascii=False) + "\n"
    old_fmt = json.dumps(json.loads(old), indent=2, ensure_ascii=False) + "\n"
    diff = "".join(difflib.unified_diff(old_fmt.splitlines(1), new.splitlines(1), "before", "after"))
    print(diff or "no changes")
    if "--write" in sys.argv and diff:
        if path.exists():
            shutil.copy2(path, path.with_name(path.name + ".bak"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8")
        print(f"written {path} (backup {path.name}.bak)")


if __name__ == "__main__":
    main()
