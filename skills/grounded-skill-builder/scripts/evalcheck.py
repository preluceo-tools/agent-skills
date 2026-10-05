"""Check an eval file against the rules in SKILL.md step 5, before any paid `claude` run.

Trigger file (has "cases"): at least 5 should_trigger true and 5 false, unique ids.
Quality file (has "scenarios"): unique ids, non-empty `files` whenever the prompt names a file or folder,
6 to 10 rubric items per scenario.
A missing or unparseable file gives one line: the cause and the fix.

usage: python evalcheck.py <eval file> [<eval file> ...]      exit code 1 when any file has an error
"""
import json, os, re, sys

EXT = "txt|md|json|py|js|ts|csv|yaml|yml|toml|xml|html|log|ini|cfg|sh|ps1|docx|pdf|xlsx|png|jpg|zip"
# a ./ ../ or ~/ path, or a word ending in a common file extension (URLs are removed first);
# a bare "yes/no" or "and/or" is not a path
NAMES_FILE = re.compile(rf"(?<![\w/.])(?:\.{{1,2}}|~)/[\w.-]+|\b[\w-]+\.(?:{EXT})\b")


def names_file(prompt):
    return bool(NAMES_FILE.search(re.sub(r"https?://\S+", "", prompt)))


def dupes(items):
    seen, out = set(), []
    for i in items:
        if i in seen and i not in out:
            out.append(i)
        seen.add(i)
    return out


def trigger_errors(cases):
    errs = [f"case id '{i}' is used more than once. Fix: give each case its own id." for i in dupes(c.get("id") for c in cases)]
    for want, label in ((True, "true"), (False, "false")):
        n = sum(c.get("should_trigger") is want for c in cases)
        if n < 5:
            errs.append(f"only {n} cases have should_trigger: {label}; need at least 5. "
                        f"Fix: add {5 - n} more built from the {'triggers' if want else 'near-misses'}.")
    for c in cases:
        if not isinstance(c.get("should_trigger"), bool):
            errs.append(f"case '{c.get('id')}': should_trigger must be true or false. Fix: set it.")
        if not c.get("prompt"):
            errs.append(f"case '{c.get('id')}': no prompt. Fix: write what a user would type.")
    return errs


def quality_errors(scenarios):
    errs = [f"scenario id '{i}' is used more than once. Fix: give each scenario its own id." for i in dupes(s.get("id") for s in scenarios)]
    for s in scenarios:
        sid = s.get("id")
        if not s.get("prompt"):
            errs.append(f"scenario '{sid}': no prompt. Fix: write what a user would type.")
        if names_file(s.get("prompt", "")) and not s.get("files"):
            errs.append(f"scenario '{sid}': the prompt names a file or folder but `files` is empty. "
                        "Fix: seed every file the prompt names, with its full contents.")
        n = len(s.get("rubric") or [])
        if not 6 <= n <= 10:
            errs.append(f"scenario '{sid}': {n} rubric items; need 6 to 10. "
                        f"Fix: {f'add {6 - n}' if n < 6 else f'merge or drop {n - 10}'}.")
    return errs


def check(path):
    """Return a list of error lines for one eval file; empty when it is well formed."""
    try:
        spec = json.load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        return [f"{path}: file not found. Fix: write it (SKILL.md step 5) or fix the path."]
    except (ValueError, OSError) as e:
        return [f"{path}: cannot read it as JSON ({e}). Fix: correct the syntax at that position."]
    if not isinstance(spec, dict):
        return [f"{path}: top level must be an object with \"skill\" and \"cases\" or \"scenarios\". Fix: wrap it."]
    items = spec.get("cases", spec.get("scenarios"))
    if isinstance(items, list) and not all(isinstance(i, dict) for i in items):
        return [f"{path}: every entry must be an object with an \"id\". Fix: check the braces around each entry."]
    if isinstance(spec.get("cases"), list):
        errs = trigger_errors(spec["cases"])
    elif isinstance(spec.get("scenarios"), list):
        errs = quality_errors(spec["scenarios"])
    else:
        errs = ["has neither a \"cases\" list (trigger evals) nor a \"scenarios\" list (quality evals). Fix: add one."]
    return [e if e.startswith(path) else f"{path}: {e}" for e in errs]


def require(path):
    """For the runners: stop with every error before any `claude` call."""
    errs = check(path)
    if errs:
        sys.exit("\n".join(errs))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    bad = [e for p in sys.argv[1:] for e in check(p)]
    print("\n".join(bad) if bad else "eval files OK")
    sys.exit(1 if bad else 0)
