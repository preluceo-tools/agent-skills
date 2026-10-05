"""Print what the user typed in Claude Code session transcripts (*.jsonl), oldest first.

Skips tool results, slash-command wrappers, skill bodies and background-task notifications,
so what remains is the user's own words: the corrections a skill is mined from.

usage: python extract_user_turns.py <transcript.jsonl> [...] [--grep WORD] [--max 1500]
Transcripts live in ~/.claude/projects/<project folder>/<session id>.jsonl.
"""
import argparse, json, os

SKIP_PREFIXES = ("<command", "<local-command", "<task-notification", "<system-reminder")


def user_turns(path):
    for line in open(path, encoding="utf-8", errors="ignore"):
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("type") != "user" or m.get("isMeta"):
            continue
        c = m.get("message", {}).get("content")
        if isinstance(c, list):
            c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
        c = (c or "").strip()
        if not c or c.startswith(SKIP_PREFIXES) or "Base directory for this skill" in c[:300]:
            continue
        yield c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcripts", nargs="+")
    ap.add_argument("--grep", help="only print sessions whose text contains this word")
    ap.add_argument("--max", type=int, default=1500, help="characters kept per turn")  # 1500: enough to read a request, short enough to scan a whole transcript
    a = ap.parse_args()
    for p in a.transcripts:
        if a.grep and a.grep not in open(p, encoding="utf-8", errors="ignore").read():
            continue
        turns = list(user_turns(p))
        print(f"######## {os.path.basename(p)}  ({len(turns)} turns)")
        for t in turns:
            print(t[: a.max])
            print("-----")


if __name__ == "__main__":
    main()
