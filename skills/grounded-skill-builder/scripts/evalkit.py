"""Shared helpers for the eval runners: call `claude -p`, parse its stream-json output."""
import json, subprocess


def claude(args, cwd, stdin=None, timeout=900):
    """Run the Claude Code CLI headless and return its stdout ('' on timeout)."""
    try:
        return subprocess.run(["claude", *args], cwd=cwd, input=stdin, capture_output=True,
                              text=True, encoding="utf-8", timeout=timeout).stdout
    except subprocess.TimeoutExpired as e:
        out = e.stdout
        return (out.decode("utf-8", "ignore") if isinstance(out, bytes) else out) or ""


def parse(stream):
    """Return (skills called, final text, error or None) from stream-json output.

    An error means the run says nothing about the skill: an API error such as a usage limit,
    or a permission prompt that a headless run cannot answer."""
    skills, final, error = [], "", None
    for line in stream.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("type") == "result":
            final = m.get("result") or ""
            if m.get("is_error") or m.get("api_error_status"):
                error = f"{m.get('api_error_status')}: {final[:120]}"
        if m.get("type") == "user" and error is None:
            for c in m.get("message", {}).get("content", []):
                text = str(c.get("content", "")) if isinstance(c, dict) and c.get("is_error") else ""
                if "requested permissions" in text:
                    error = "permission prompt: " + text[:120]
        if m.get("type") == "assistant":
            for c in m["message"].get("content", []):
                if c.get("type") == "tool_use" and c.get("name") == "Skill":
                    skills.append(c.get("input", {}).get("skill", ""))
    if not stream.strip():
        error = "no output (timeout or CLI failure)"
    return skills, final, error


def called(skills, name):
    """True when the skill was invoked by name, with or without a plugin prefix."""
    return any(s == name or s.endswith(":" + name) for s in skills)


def run_root(out, prefix):
    """The folder the runs go in, as a full long path: Claude Code blocks paths with short 8.3 names such as ABCDEF~1."""
    import os, tempfile
    root = out or tempfile.mkdtemp(prefix=prefix)
    os.makedirs(root, exist_ok=True)
    return os.path.realpath(root)
