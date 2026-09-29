"""Run a skill's evals/trigger-evals.json through `claude -p` and report whether the skill fired.

Each trial runs in its own empty folder with file-writing and shell tools blocked, so a prompt
cannot change anything. A case counts as triggered only when the Skill tool was called with the
skill's name. Runs that end in an API error (e.g. a usage limit) or stop at a permission prompt are INVALID, not failures.

--pilot runs one trial of one positive and one negative case, prints the cost estimate for the
full plan the other flags describe, and exits. Pass the same --out to the full run to reuse the pilot's runs.
Every run ends with the actual totals: notional USD and the five-hour window used.

usage: python run_trigger_evals.py <skill folder> [--trials 3] [--out <folder>] [--parallel 5] [--pilot]
"""
import argparse, concurrent.futures as cf, json, os
from evalkit import claude, parse, called, run_root, show_spent, report_pilot

BLOCKED = ["Bash", "PowerShell", "Edit", "Write", "NotebookEdit", "Agent"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--out", default=None, help="where run folders go (default: a new temp folder)")
    ap.add_argument("--parallel", type=int, default=5)
    ap.add_argument("--pilot", action="store_true", help="estimate the cost of the full run from a small slice, then exit")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(a.skill_dir, "evals", "trigger-evals.json"), encoding="utf-8"))
    name, out = spec["skill"], run_root(a.out, "trigger-evals-")

    def run(case, n):
        d = os.path.join(out, f"{case['id']}-{n}")
        os.makedirs(d, exist_ok=True)
        t, mark = os.path.join(d, "_transcript.jsonl"), os.path.join(d, "_pilot")
        if os.path.exists(mark) and not a.pilot:  # a pilot run counts toward the full run
            os.remove(mark)
            skills, _, error, cost = parse(open(t, encoding="utf-8").read())
            if not error:
                return case, n, called(skills, name), None, None
        stream = claude(["-p", case["prompt"], "--output-format", "stream-json", "--verbose",
                         "--no-session-persistence", "--disallowedTools", *BLOCKED], d)
        open(t, "w", encoding="utf-8").write(stream)
        if a.pilot:
            open(mark, "w").close()
        skills, _, error, cost = parse(stream)
        return case, n, None if error else called(skills, name), error, cost

    jobs = [(c, n) for c in spec["cases"] for n in range(a.trials)]
    planned = len(jobs)
    if a.pilot:
        jobs = [(next(c for c in spec["cases"] if c["should_trigger"] is want), 0) for want in (True, False)]
    with cf.ThreadPoolExecutor(a.parallel) as ex:
        res = list(ex.map(lambda j: run(*j), jobs))
    costs = [r[4] for r in res if r[4]]
    res = [r[:4] for r in res]
    if a.pilot:
        return report_pilot(costs, len(jobs), planned, out)

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
    print(show_spent(costs))


if __name__ == "__main__":
    main()
