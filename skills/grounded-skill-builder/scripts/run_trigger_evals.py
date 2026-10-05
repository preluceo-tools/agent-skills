"""Run a skill's evals/trigger-evals.json through `claude -p` and report whether the skill fired.

Each trial runs in its own empty folder with file-writing and shell tools blocked, so a prompt
cannot change anything. A case counts as triggered only when the Skill tool was called with the
skill's name. Runs that end in an API error (e.g. a usage limit) or stop at a permission prompt are INVALID, not failures.

--pilot runs one trial of one positive and one negative case, prints the cost estimate for the
full plan the other flags describe, and exits. Pass the same --out to the full run to reuse the pilot's runs.
Every run ends with the actual totals: notional USD and the five-hour window used.

usage: python run_trigger_evals.py <skill folder> [--trials 3] [--models haiku,sonnet] [--out <folder>] [--parallel 5] [--pilot]
"""
import argparse, concurrent.futures as cf, json, os
from evalcheck import require
from evalkit import claude, parse, called, run_root, show_spent, report_pilot, model_args, parse_models, label, folder_tag

BLOCKED = ["Bash", "PowerShell", "Edit", "Write", "NotebookEdit", "Agent"]


def run_args(prompt, model=None):
    return ["-p", prompt, "--output-format", "stream-json", "--verbose", "--no-session-persistence",
            *model_args(model), "--disallowedTools", *BLOCKED]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("--trials", type=int, default=3)  # 3: one odd run shows up against the other two
    ap.add_argument("--models", default="", help="comma-separated models, e.g. haiku,sonnet (alias or full name); default: the model in use")
    ap.add_argument("--out", default=None, help="where run folders go (default: a new temp folder)")
    ap.add_argument("--parallel", type=int, default=5)  # 5: enough overlap to save time, few enough to stay clear of rate limits
    ap.add_argument("--pilot", action="store_true", help="estimate the cost of the full run from a small slice, then exit")
    a = ap.parse_args()
    path = os.path.join(a.skill_dir, "evals", "trigger-evals.json")
    require(path)  # before any paid call
    spec = json.load(open(path, encoding="utf-8"))
    name, out, models = spec["skill"], run_root(a.out, "trigger-evals-"), parse_models(a.models)

    def run(case, n, model):
        d = os.path.join(out, f"{case['id']}-{n}{folder_tag(model)}")
        os.makedirs(d, exist_ok=True)
        t, mark = os.path.join(d, "_transcript.jsonl"), os.path.join(d, "_pilot")
        if os.path.exists(mark) and not a.pilot:  # a pilot run counts toward the full run
            os.remove(mark)
            skills, _, error, cost = parse(open(t, encoding="utf-8").read())
            if not error:
                return case, n, model, called(skills, name), None, None
        stream = claude(run_args(case["prompt"], model), d)
        open(t, "w", encoding="utf-8").write(stream)
        if a.pilot:
            open(mark, "w").close()
        skills, _, error, cost = parse(stream)
        return case, n, model, None if error else called(skills, name), error, cost

    jobs = [(c, n, m) for m in models for c in spec["cases"] for n in range(a.trials)]
    planned = len(jobs)
    if a.pilot:
        jobs = [(next(c for c in spec["cases"] if c["should_trigger"] is want), 0, m) for m in models for want in (True, False)]
    with cf.ThreadPoolExecutor(a.parallel) as ex:
        res = list(ex.map(lambda j: run(*j), jobs))
    costs = [r[5] for r in res if r[5]]
    res = [r[:5] for r in res]
    if a.pilot:
        return report_pilot(costs, len(jobs), planned, out, len(models))

    rows, wrong, invalid = {}, 0, 0
    for case, n, model, hit, error in res:
        mark = "?" if hit is None else ("Y" if hit else "n")
        rows.setdefault(label(case["id"], model), [case["should_trigger"], ""])[1] += mark
        invalid += hit is None
        wrong += hit is not None and hit != case["should_trigger"]
    print(f"{'case':14} expect  runs")
    for cid, (expect, marks) in rows.items():
        print(f"{cid:14} {'fire' if expect else 'quiet':6}  {marks}")
    print(f"\n{wrong} wrong, {invalid} invalid (Y fired, n quiet, ? API error) of {len(res)} runs. Run folders: {out}")
    json.dump([{"id": c["id"], "trial": n, "should": c["should_trigger"], "model": m, "fired": h, "error": e} for c, n, m, h, e in res],
              open(os.path.join(out, "_results.json"), "w", encoding="utf-8"), indent=1)
    print(show_spent(costs))


if __name__ == "__main__":
    main()
