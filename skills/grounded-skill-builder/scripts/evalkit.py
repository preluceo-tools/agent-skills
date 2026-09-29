"""Shared helpers for the eval runners: call `claude -p`, parse its stream-json output, measure its cost."""
import datetime, json, subprocess


def claude(args, cwd, stdin=None, timeout=900):
    """Run the Claude Code CLI headless and return its stdout ('' on timeout)."""
    try:
        return subprocess.run(["claude", *args], cwd=cwd, input=stdin, capture_output=True,
                              text=True, encoding="utf-8", timeout=timeout).stdout
    except subprocess.TimeoutExpired as e:
        out = e.stdout
        return (out.decode("utf-8", "ignore") if isinstance(out, bytes) else out) or ""


def parse(stream):
    """Return (skills called, final text, error or None, cost) from stream-json output.

    An error means the run says nothing about the skill: an API error such as a usage limit,
    or a permission prompt that a headless run cannot answer.
    cost is {"usd", "util", "resets"}: the run's notional USD, and the five-hour window's
    utilization (0-1) and reset time (epoch seconds); util and resets are None on an API-key account."""
    skills, final, error = [], "", None
    cost = {"usd": 0.0, "util": None, "resets": None}
    for line in stream.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("type") == "rate_limit_event":
            w = (m.get("rate_limit_info") or {}).get("unifiedWindows", {}).get("five_hour")
            if w and w.get("utilization") is not None:
                cost["util"], cost["resets"] = w["utilization"], w.get("resetsAt")
        if m.get("type") == "result":
            final = m.get("result") or ""
            cost["usd"] = m.get("total_cost_usd") or 0.0
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
    return skills, final, error, cost


def estimate(pilot_usd, pilot_runs, planned_runs, util_before, util_after, resets):
    """Extrapolate a pilot to the full plan. The pilot's own runs count toward the plan.

    The five-hour window moves in 1% steps: a pilot that moved it less than one step (sub1)
    gives an upper bound, one step per pilot. util_before None means an API-key account."""
    scale = planned_runs / pilot_runs
    e = {"usd": pilot_usd * scale, "window": None, "end": None, "resets": resets, "sub1": False, "over90": False}
    if util_before is None or util_after is None:
        return e
    step = util_after - util_before
    e["sub1"] = step < 0.01
    step = max(step, 0.01)
    e["window"] = step * scale
    e["end"] = util_after + step * (planned_runs - pilot_runs) / pilot_runs
    e["over90"] = e["end"] > 0.9
    return e


def local_time(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime("%H:%M") if epoch else "?"


def show_estimate(e, planned_runs):
    """The Eval cost warning text for an estimate()."""
    lines = [f"ESTIMATE for the full plan, {planned_runs} runs: about ${e['usd']:.2f} notional USD."]
    if e["window"] is not None:
        bound = "at most " if e["sub1"] else "about "
        lines.append(f"Five-hour window: {bound}{e['window']:.0%} of it; ends near {min(e['end'], 1):.0%} "
                     f"(resets {local_time(e['resets'])} local time). Every session on the account shares it.")
        if e["sub1"]:
            lines.append("The pilot moved the window less than its 1% step, so the window figure is an upper bound.")
        if e["over90"]:
            lines.append("WARNING: the run would end above 90% of the window. Use fewer trials, an --only subset, "
                         "or wait until the reset.")
    return "\n".join(lines)


def show_spent(costs):
    """Actual totals over a list of parse() costs: USD, and the window used when the account has one."""
    usd = sum(c["usd"] for c in costs)
    utils = [c["util"] for c in costs if c["util"] is not None]
    if not utils:
        return f"SPENT: ${usd:.2f} notional USD."
    # ponytail: window used = spread of the readings each run saw at its start; misses the last run's share, 1% steps
    resets = max(c["resets"] or 0 for c in costs)
    return (f"SPENT: ${usd:.2f} notional USD; five-hour window used about {max(utils) - min(utils):.0%}, "
            f"now {max(utils):.0%} (resets {local_time(resets)} local time).")


def probe(cwd):
    """One minimal run, to read the five-hour window now. Returns its parse() cost."""
    return parse(claude(["-p", "Reply with OK", "--output-format", "stream-json", "--verbose",
                         "--no-session-persistence", "--tools", ""], cwd, timeout=300))[3]


def called(skills, name):
    """True when the skill was invoked by name, with or without a plugin prefix."""
    return any(s == name or s.endswith(":" + name) for s in skills)


def run_root(out, prefix):
    """The folder the runs go in, as a full long path: Claude Code blocks paths with short 8.3 names such as ABCDEF~1."""
    import os, tempfile
    root = out or tempfile.mkdtemp(prefix=prefix)
    os.makedirs(root, exist_ok=True)
    return os.path.realpath(root)


def report_pilot(costs, pilot_runs, planned_runs, out):
    """Print the Eval cost warning for a finished pilot: its runs' costs, then one probe for the window after it."""
    after = probe(out)
    utils = [c["util"] for c in costs if c["util"] is not None]
    print(show_estimate(estimate(sum(c["usd"] for c in costs), pilot_runs, planned_runs,
                                 min(utils, default=None), after["util"], after["resets"]), planned_runs))
    print(show_spent(costs + [after]) + f"   Pilot run folders: {out} (pass --out {out} to the full run to reuse them)")
