"""Run a skill's evals/trigger-evals.json through `claude -p` and report whether the skill fired.

Each trial runs in its own empty folder with file-writing and shell tools blocked, so a prompt
cannot change anything. A case counts as triggered only when the Skill tool was called with the
skill's name. Runs that end in an API error (e.g. a usage limit) or stop at a permission prompt are INVALID, not failures.

usage: python run_trigger_evals.py <skill folder> [--trials 3] [--out <folder>] [--parallel 5]
"""
import argparse, concurrent.futures as cf, json, os
from evalkit import claude, parse, called, run_root

BLOCKED = ["Bash", "PowerShell", "Edit", "Write", "NotebookEdit", "Agent"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--out", default=None, help="where run folders go (default: a new temp folder)")
    ap.add_argument("--parallel", type=int, default=5)
    a = ap.parse_args()
    spec = json.load(open(os.path.join(a.skill_dir, "evals", "trigger-evals.json"), encoding="utf-8"))
    name, out = spec["skill"], run_root(a.out, "trigger-evals-")

    def run(case, n):
        d = os.path.join(out, f"{case['id']}-{n}")
        os.makedirs(d, exist_ok=True)
        stream = claude(["-p", case["prompt"], "--output-format", "stream-json", "--verbose",
                         "--no-session-persistence", "--disallowedTools", *BLOCKED], d)
        open(os.path.join(d, "_transcript.jsonl"), "w", encoding="utf-8").write(stream)
        skills, _, error = parse(stream)
        return case, n, None if error else called(skills, name), error

    jobs = [(c, n) for c in spec["cases"] for n in range(a.trials)]
    with cf.ThreadPoolExecutor(a.parallel) as ex:
        res = list(ex.map(lambda j: run(*j), jobs))

    rows, wrong, invalid = {}, 0, 0
    for case, n, hit, error in res:
        mark = "?" if hit is None else ("Y" if hit else "n")
        rows.setdefault(case["id"], [case["should_trigger"], ""])[1] += mark
        invalid += hit is None
        wrong += hit is not None and hit != case["should_trigger"]
    print(f"{'case':14} expect  runs")
    for cid, (expect, marks) in rows.items():
        print(f"{cid:14} {'fire' if expect else 'quiet':6}  {marks}")
    print(f"\n{wrong} wrong, {invalid} invalid (Y fired, n quiet, ? API error) of {len(res)} runs. Run folders: {out}")
    json.dump([{"id": c["id"], "trial": n, "should": c["should_trigger"], "fired": h, "error": e} for c, n, h, e in res],
              open(os.path.join(out, "_results.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
