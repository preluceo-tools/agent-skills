#!/usr/bin/env python3
"""Smoke check for apply_settings.py: merge, backup, refusals. Prints 'ok' or fails."""
import json, subprocess, sys, tempfile
from pathlib import Path

SCRIPT = str(Path(__file__).with_name("apply_settings.py"))


def run(settings, plan, write=False):
    with tempfile.TemporaryDirectory() as t:
        s, p = Path(t) / "settings.json", Path(t) / "plan.json"
        s.write_text(json.dumps(settings), encoding="utf-8")
        p.write_text(json.dumps(plan), encoding="utf-8")
        r = subprocess.run([sys.executable, SCRIPT, str(s), str(p)] + (["--write"] if write else []), capture_output=True, text=True)
        return r, json.loads(s.read_text(encoding="utf-8")), (json.loads(s.with_name("settings.json.bak").read_text(encoding="utf-8")) if s.with_name("settings.json.bak").exists() else None)


base = {"model": "opus", "env": {"FOO": "1"}, "permissions": {"allow": ["Bash(git status)"], "deny": ["WebFetch"]}}
plan = {"deny": ["NotebookEdit"], "flags": {"disableWorkflows": True}, "skillOverrides": {"dataviz": "off"}}

r, out, bak = run(base, plan, write=True)
assert r.returncode == 0, r.stderr
assert out["model"] == "opus" and out["env"] == {"FOO": "1"}, "existing keys kept"
assert out["permissions"]["allow"] == ["Bash(git status)"]
assert out["permissions"]["deny"] == ["WebFetch", "NotebookEdit"]
assert out["disableWorkflows"] is True and out["skillOverrides"] == {"dataviz": "off"}
assert bak == base, "backup holds original"

r, out, bak = run(base, plan)
assert out == base and bak is None, "no write without --write"

for bad in ({"deny": ["Bash"]}, {"deny": ["AskUserQuestion"]}, {"deny": ["Bash(rm *)"]},
            {"flags": {"disableNothing": True}}, {"skillOverrides": {"x": "maybe"}}):
    r, _, _ = run(base, bad)
    assert r.returncode != 0 and "refused" in r.stderr, f"must refuse {bad}"
print("ok")
