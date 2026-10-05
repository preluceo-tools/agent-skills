"""Run a skill's evals/quality-evals.json with and without the skill, and grade each run blind.

For every scenario and condition, a trial seeds the scenario's files into an empty folder, runs
the prompt through `claude -p` (edits allowed inside that folder, shell and subagents blocked),
then a separate `claude -p` call with no tools grades the result against the rubric without
knowing the condition. Seeded files are hashed, so the grader sees whether any was modified.

The baseline uses --disable-slash-commands, which turns off ALL skills, not only this one.
Runs that end in an API error (e.g. a usage limit) or stop at a permission prompt are INVALID and left out of the scores.

--pilot runs one scenario, one trial, every condition, graded; prints the cost estimate for the
full plan the other flags describe, and exits. Pass the same --out to the full run to reuse the pilot's runs.
--models runs everything on each model named (an alias such as haiku, or a full name), the grader included; the
default is the model in use. The pilot runs its slice on every model, so the estimate is per model and the plan multiplies by the count.
Every run ends with the actual totals: notional USD and the five-hour window used, grader calls included.

usage: python run_quality_evals.py <skill folder> [--trials 2] [--only id,id] [--conds skill,noskill]
                                   [--models haiku,sonnet] [--out <folder>] [--parallel 5] [--pilot]
"""
import argparse, concurrent.futures as cf, hashlib, json, os, re
from evalcheck import require
from evalkit import claude, parse, called, run_root, show_spent, report_pilot, model_args, parse_models, label, folder_tag

BLOCKED = ["Bash", "PowerShell", "Agent", "WebSearch", "WebFetch"]


def sha(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest()


def run_args(prompt, cond, skill_dir, model=None):
    """The `claude` arguments for one scenario run."""
    args = ["-p", prompt, "--output-format", "stream-json", "--verbose", "--no-session-persistence",
            "--permission-mode", "acceptEdits", *model_args(model), "--disallowedTools", *BLOCKED]
    if cond == "noskill":
        args.append("--disable-slash-commands")
    else:
        # the skill loads from its installed copy, and runs look around the skills folder to find it, so they may read all of it
        skills = os.path.join(os.path.expanduser("~"), ".claude", "skills")
        args += ["--add-dir", os.path.realpath(skill_dir)] + (["--add-dir", os.path.realpath(skills)] if os.path.isdir(skills) else [])
    return args


def grader_args(model=None):
    return ["-p", "--disable-slash-commands", "--no-session-persistence", "--tools", "",
            "--output-format", "stream-json", "--verbose", *model_args(model)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("--trials", type=int, default=2)  # 2: quality runs cost more than trigger runs; two show run-to-run spread
    ap.add_argument("--only", default="", help="comma-separated scenario ids")
    ap.add_argument("--conds", default="skill,noskill")
    ap.add_argument("--models", default="", help="comma-separated models, e.g. haiku,sonnet (alias or full name); default: the model in use")
    ap.add_argument("--out", default=None)
    ap.add_argument("--parallel", type=int, default=5)  # 5: enough overlap to save time, few enough to stay clear of rate limits
    ap.add_argument("--pilot", action="store_true", help="estimate the cost of the full run from a small slice, then exit")
    a = ap.parse_args()
    path = os.path.join(a.skill_dir, "evals", "quality-evals.json")
    require(path)  # before any paid call
    spec = json.load(open(path, encoding="utf-8"))
    name, out, models = spec["skill"], run_root(a.out, "quality-evals-"), parse_models(a.models)
    scen = [s for s in spec["scenarios"] if not a.only or s["id"] in a.only.split(",")]
    costs = []

    def run(sc, cond, n, model):
        d = os.path.join(out, f"{sc['id']}-{cond}-{n}{folder_tag(model)}")
        os.makedirs(d, exist_ok=True)
        mark, grade = os.path.join(d, "_pilot"), os.path.join(d, "_grade.json")
        if os.path.exists(mark) and not a.pilot:  # a graded pilot run counts toward the full run
            os.remove(mark)
            if os.path.exists(grade):
                g = json.load(open(grade, encoding="utf-8"))
                return sc, label(cond, model), n, {s.get("n"): s for s in g["scores"]}, None, g["skills"]
        for rel, txt in sc.get("files", {}).items():
            p = os.path.join(d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8").write(txt)
        before = {rel: sha(os.path.join(d, rel)) for rel in sc.get("files", {})}
        args = run_args(sc["prompt"], cond, a.skill_dir, model)
        stream = claude(args, d)
        open(os.path.join(d, "_transcript.jsonl"), "w", encoding="utf-8").write(stream)
        skills, final, error, cost = parse(stream)
        costs.append(cost)
        if error:
            return sc, label(cond, model), n, None, error, skills
        changed = [r for r in before if not os.path.exists(os.path.join(d, r)) or sha(os.path.join(d, r)) != before[r]]
        bundle = [f"FINAL ASSISTANT MESSAGE:\n{final}\n", f"SEEDED FILES MODIFIED: {changed or 'none'}\n"]
        for root, _, fs in os.walk(d):
            for f in sorted(fs):
                rel = os.path.relpath(os.path.join(root, f), d).replace("\\", "/")
                if not rel.startswith("_") and rel not in before:
                    bundle.append(f"=== NEW FILE {rel} ===\n" + open(os.path.join(d, rel), encoding="utf-8", errors="ignore").read()[:60000])  # 60000 chars per new file: keeps the grader prompt inside its context
        rubric = "\n".join(f"{i + 1}. {r}" for i, r in enumerate(sc["rubric"]))
        judge = ("You are grading an AI assistant's work. The user prompt was:\n<<<\n" + sc["prompt"] + "\n>>>\n\n"
                 "Below is everything it produced.\n\n" + "\n".join(bundle) +
                 "\n\nGrade each criterion strictly from the evidence; read any code to decide what it really does. Criteria:\n"
                 + rubric + '\n\nReply with only JSON: {"scores":[{"n":1,"pass":true,"why":"<12 words"}, ...]}')
        verdict = claude(grader_args(model), d, stdin=judge, timeout=600)  # 600 s: the grader reads the whole bundle but edits nothing
        _, verdict, grader_error, cost = parse(verdict)
        costs.append(cost)
        try:
            scores = json.loads(re.search(r"\{.*\}", verdict, re.S).group(0))["scores"]
        except (AttributeError, ValueError, KeyError):
            return sc, label(cond, model), n, None, "grader reply unreadable: " + (grader_error or verdict[-200:]), skills
        json.dump({"scores": scores, "changed": changed, "skills": skills}, open(grade, "w", encoding="utf-8"), indent=1)
        if a.pilot:
            open(mark, "w").close()
        return sc, label(cond, model), n, {s.get("n"): s for s in scores}, None, skills

    conds = a.conds.split(",")
    jobs = [(s, c, n, m) for m in models for s in scen for c in conds for n in range(a.trials)]
    planned = len(jobs)
    if a.pilot:
        scen, jobs = scen[:1], [(scen[0], c, 0, m) for m in models for c in conds]
    with cf.ThreadPoolExecutor(a.parallel) as ex:
        res = list(ex.map(lambda j: run(*j), jobs))
    if a.pilot:
        return report_pilot(costs, len(jobs), planned, out, len(models))

    cols = [label(c, m) for m in models for c in conds]
    totals = {c: [0, 0] for c in cols}
    for sc in scen:
        print(f"## {sc['id']}")
        for i, crit in enumerate(sc["rubric"], 1):
            cells = []
            for c in cols:
                marks = ""
                for s, cond, n, scores, error, _ in res:
                    if s is sc and cond == c:
                        if scores is None:
                            marks += "?"
                            continue
                        ok = bool(scores.get(i, {}).get("pass"))
                        marks += "Y" if ok else "n"
                        totals[c][0] += ok
                        totals[c][1] += 1
                cells.append(f"{c}={marks:<4}")
            print(f"  {i:2} {' '.join(cells)} {crit[:90]}")
    for s, cond, n, scores, error, skills in res:
        if error:
            print(f"INVALID {s['id']}-{cond}-{n}: {error}")
        elif cond.split("@")[0] == "skill" and not called(skills, name):
            print(f"NOTE {s['id']}-{cond}-{n}: the skill was not invoked in this run")
    print("\n" + ", ".join(f"{c}: {p}/{t} points" for c, (p, t) in totals.items()) + f"   (Y pass, n fail, ? invalid). Run folders: {out}")
    print(show_spent(costs))


if __name__ == "__main__":
    main()
