"""Run a skill's evals/quality-evals.json with and without the skill, and grade each run blind.

For every scenario and condition, a trial seeds the scenario's files into an empty folder, runs
the prompt through `claude -p` (edits allowed inside that folder, shell and subagents blocked),
then a separate `claude -p` call with no tools grades the result against the rubric without
knowing the condition. Seeded files are hashed, so the grader sees whether any was modified.

The baseline uses --disable-slash-commands, which turns off ALL skills, not only this one.
Runs that end in an API error (e.g. a usage limit) or stop at a permission prompt are INVALID and left out of the scores.

--pilot runs one scenario, one trial, every condition, graded; prints the cost estimate for the
full plan the other flags describe, and exits. Pass the same --out to the full run to reuse the pilot's runs.
Every run ends with the actual totals: notional USD and the five-hour window used, grader calls included.

usage: python run_quality_evals.py <skill folder> [--trials 2] [--only id,id] [--conds skill,noskill]
                                   [--out <folder>] [--parallel 5] [--pilot]
"""
import argparse, concurrent.futures as cf, hashlib, json, os, re
from evalkit import claude, parse, called, run_root, show_spent, report_pilot

BLOCKED = ["Bash", "PowerShell", "Agent", "WebSearch", "WebFetch"]


def sha(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--only", default="", help="comma-separated scenario ids")
    ap.add_argument("--conds", default="skill,noskill")
    ap.add_argument("--out", default=None)
    ap.add_argument("--parallel", type=int, default=5)
    ap.add_argument("--pilot", action="store_true", help="estimate the cost of the full run from a small slice, then exit")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(a.skill_dir, "evals", "quality-evals.json"), encoding="utf-8"))
    name, out = spec["skill"], run_root(a.out, "quality-evals-")
    scen = [s for s in spec["scenarios"] if not a.only or s["id"] in a.only.split(",")]
    costs = []

    def run(sc, cond, n):
        d = os.path.join(out, f"{sc['id']}-{cond}-{n}")
        os.makedirs(d, exist_ok=True)
        mark, grade = os.path.join(d, "_pilot"), os.path.join(d, "_grade.json")
        if os.path.exists(mark) and not a.pilot:  # a graded pilot run counts toward the full run
            os.remove(mark)
            if os.path.exists(grade):
                g = json.load(open(grade, encoding="utf-8"))
                return sc, cond, n, {s.get("n"): s for s in g["scores"]}, None, g["skills"]
        for rel, txt in sc.get("files", {}).items():
            p = os.path.join(d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8").write(txt)
        before = {rel: sha(os.path.join(d, rel)) for rel in sc.get("files", {})}
        args = ["-p", sc["prompt"], "--output-format", "stream-json", "--verbose", "--no-session-persistence",
                "--permission-mode", "acceptEdits", "--disallowedTools", *BLOCKED]
        if cond == "noskill":
            args.append("--disable-slash-commands")
        else:
            # the skill loads from its installed copy, and runs look around the skills folder to find it, so they may read all of it
            skills = os.path.join(os.path.expanduser("~"), ".claude", "skills")
            args += ["--add-dir", os.path.realpath(a.skill_dir)] + (["--add-dir", os.path.realpath(skills)] if os.path.isdir(skills) else [])
        stream = claude(args, d)
        open(os.path.join(d, "_transcript.jsonl"), "w", encoding="utf-8").write(stream)
        skills, final, error, cost = parse(stream)
        costs.append(cost)
        if error:
            return sc, cond, n, None, error, skills
        changed = [r for r in before if not os.path.exists(os.path.join(d, r)) or sha(os.path.join(d, r)) != before[r]]
        bundle = [f"FINAL ASSISTANT MESSAGE:\n{final}\n", f"SEEDED FILES MODIFIED: {changed or 'none'}\n"]
        for root, _, fs in os.walk(d):
            for f in sorted(fs):
                rel = os.path.relpath(os.path.join(root, f), d).replace("\\", "/")
                if not rel.startswith("_") and rel not in before:
                    bundle.append(f"=== NEW FILE {rel} ===\n" + open(os.path.join(d, rel), encoding="utf-8", errors="ignore").read()[:60000])
        rubric = "\n".join(f"{i + 1}. {r}" for i, r in enumerate(sc["rubric"]))
        judge = ("You are grading an AI assistant's work. The user prompt was:\n<<<\n" + sc["prompt"] + "\n>>>\n\n"
                 "Below is everything it produced.\n\n" + "\n".join(bundle) +
                 "\n\nGrade each criterion strictly from the evidence; read any code to decide what it really does. Criteria:\n"
                 + rubric + '\n\nReply with only JSON: {"scores":[{"n":1,"pass":true,"why":"<12 words"}, ...]}')
        verdict = claude(["-p", "--disable-slash-commands", "--no-session-persistence", "--tools", "",
                          "--output-format", "stream-json", "--verbose"], d, stdin=judge, timeout=600)
        _, verdict, grader_error, cost = parse(verdict)
        costs.append(cost)
        try:
            scores = json.loads(re.search(r"\{.*\}", verdict, re.S).group(0))["scores"]
        except (AttributeError, ValueError, KeyError):
            return sc, cond, n, None, "grader reply unreadable: " + (grader_error or verdict[-200:]), skills
        json.dump({"scores": scores, "changed": changed, "skills": skills}, open(grade, "w", encoding="utf-8"), indent=1)
        if a.pilot:
            open(mark, "w").close()
        return sc, cond, n, {s.get("n"): s for s in scores}, None, skills

    conds = a.conds.split(",")
    jobs = [(s, c, n) for s in scen for c in conds for n in range(a.trials)]
    planned = len(jobs)
    if a.pilot:
        scen, jobs = scen[:1], [(scen[0], c, 0) for c in conds]
    with cf.ThreadPoolExecutor(a.parallel) as ex:
        res = list(ex.map(lambda j: run(*j), jobs))
    if a.pilot:
        return report_pilot(costs, len(jobs), planned, out)

    totals = {c: [0, 0] for c in conds}
    for sc in scen:
        print(f"## {sc['id']}")
        for i, crit in enumerate(sc["rubric"], 1):
            cells = []
            for c in conds:
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
        elif cond == "skill" and not called(skills, name):
            print(f"NOTE {s['id']}-skill-{n}: the skill was not invoked in this run")
    print("\n" + ", ".join(f"{c}: {p}/{t} points" for c, (p, t) in totals.items()) + f"   (Y pass, n fail, ? invalid). Run folders: {out}")
    print(show_spent(costs))


if __name__ == "__main__":
    main()
