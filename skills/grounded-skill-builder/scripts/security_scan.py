"""Security scan of a skill folder: Cisco skill-scanner (static analyzers only) plus a grep layer.

Prints JSON: {"skill", "findings": [{"location", "rule", "severity", "detail"}], "blocking", "evals_hold"}.
Severity is blocking (stop the step), fix (fix or justify) or note (check against the Scripts section).
evals_hold is true when the scanner could not run: evals wait for the user's go-ahead.
A clean result is best-effort, not proof of safety. Exit code 1 when any Finding is blocking.

Given a folder of skills (no SKILL.md of its own; e.g. a plugin or a skills folder), it scans every
folder below it that holds a SKILL.md and prints {"skills": [<one result per skill>], "blocking", "evals_hold"}.

usage: python security_scan.py <skill folder | folder of skills> [--native-tls]
"""
import argparse, json, os, re, subprocess, sys

# Pinned to the version verified against these flags; a bump is deliberate: re-run test_scripts.py first.
SCANNER = ["uvx", "--from", "cisco-ai-skill-scanner==2.1.0", "skill-scanner"]
SEVERITY = {"CRITICAL": "blocking", "HIGH": "blocking", "MEDIUM": "fix"}  # LOW, INFO: note

# Zero-width, bidirectional-override, invisible-operator, byte-order-mark and tag characters.
HIDDEN = "".join(chr(a) + "-" + chr(b) for a, b in [(0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x2064),
                                                    (0x2066, 0x2069), (0xFEFF, 0xFEFF), (0xE0000, 0xE007F)])
# (rule, severity, pattern, detail). The [x] classes keep this file from matching itself.
GREP = [
    ("hidden-unicode", "blocking", re.compile("[%s]" % HIDDEN),
     "invisible or bidirectional Unicode character: text the reader does not see"),
    ("base64-blob", "fix", re.compile(r"[A-Za-z0-9+/]{200,}={0,2}"), "long base64 blob: decode it and check what it holds"),
    ("download-execute", "blocking", re.compile(
        r"\b(curl|wget|iwr|irm|Invoke-WebRequest|Invoke-RestMethod)\b[^\n|]*\|\s*(sudo\s+)?(ba|z)?sh\b"
        r"|\b(curl|wget|iwr|irm|Invoke-WebRequest|Invoke-RestMethod)\b[^\n|]*\|\s*(python3?|iex|Invoke-Expression|node|perl|ruby)\b"
        r"|<\(\s*(curl|wget)\b|\$\(\s*(curl|wget)\b", re.I), "downloads code and runs it"),
    ("credential-file", "blocking", re.compile(
        r"\.aws[\\/]credential[s]|\.ssh[\\/]id_|\.net[r]c\b|\.git-credential[s]|\.pypir[c]|\.npmr[c]|\.docker[\\/]config\.json"
        r"|\.kube[\\/]config|Login[ ]Data|\.claude[\\/]\.credentials|key[c]hain", re.I), "reads a credential file"),
    ("credential-env", "fix", re.compile(r"\b[A-Z0-9_]*(API_KE[Y]|SECRE[T]|TOKE[N]|PASSWOR[D]|PASSW[D]|ACCESS_KE[Y]|PRIVATE_KE[Y])[A-Z0-9_]*\b"),
     "names a credential environment variable: the Scripts section must declare it"),
    ("network-host", "note", re.compile(r"\b(?:https?|wss?|ftp)://([A-Za-z0-9.-]+)"),
     "network host: the Scripts section must declare it if a script reaches it"),
]


def grep(root):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in files:
            p = os.path.join(dirpath, f)
            try:
                text = open(p, encoding="utf-8-sig").read()  # a leading BOM is not hidden text
            except (UnicodeDecodeError, OSError):
                continue
            rel = os.path.relpath(p, root).replace("\\", "/")
            prose = f.endswith((".md", ".txt")) or f.startswith("LICENSE")  # hosts matter only where code reaches them
            for i, line in enumerate(text.splitlines(), 1):
                for rule, sev, rx, detail in GREP:
                    m = rx.search(line)
                    if m and not (rule == "network-host" and prose):
                        shown = m.group(1) if rule == "network-host" else ascii(m.group(0))[:80]
                        yield {"location": f"{rel}:{i}", "rule": rule, "severity": sev, "detail": f"{detail}: {shown}"}


def cannot_run(cmd, error):
    low = error.lower()
    if error.startswith("FileNotFoundError"):
        cause, fix = "uv is not installed", "install uv (https://docs.astral.sh/uv/), then re-run"
    elif "unknownissuer" in low or "certificate" in low or "tls" in low:
        cause, fix = "TLS failure: a proxy or antivirus replaces the certificate", "re-run this script with --native-tls, which passes it to uvx to use the system certificate store"
    elif any(w in low for w in ("connect", "resolve", "dns", "network", "timed out", "offline")):
        cause, fix = "no network: uvx downloads the scanner from pypi.org", "connect and re-run; once downloaded, the scanner is cached"
    else:
        cause, fix = "the scanner failed to install or crashed without a report", "run the command by hand and read its error"
    return {"location": "skill-scanner", "rule": "scanner-cannot-run", "severity": "fix",
            "detail": f"the scan is incomplete: {cause}. Fix: {fix}.",
            "command": " ".join(cmd), "error": error.strip()[-1500:]}


def scanner(root, cmd):
    cmd = cmd + ["scan", root, "--format", "json", "--compact", "--fail-on-severity", "high"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=900)  # 15 min: the first run downloads the scanner before it scans
    except (OSError, subprocess.TimeoutExpired) as e:
        return [cannot_run(cmd, f"{type(e).__name__}: {e}")]
    try:
        report = json.loads(p.stdout)
    except ValueError:
        return [cannot_run(cmd, p.stderr or p.stdout or f"exit code {p.returncode}, no output")]
    return [{"location": f"{(f.get('file_path') or '?').replace(chr(92), '/')}:{f.get('line_number') or ''}".rstrip(":"),
             "rule": f"skill-scanner/{f.get('rule_id')}", "severity": SEVERITY.get(f.get("severity"), "note"),
             "detail": f.get("title") or f.get("description") or ""} for f in report.get("findings", [])]


def scan(root, cmd=SCANNER):
    findings = scanner(root, cmd) + list(grep(root))
    return {"skill": os.path.basename(os.path.realpath(root)), "findings": findings,
            "blocking": sum(f["severity"] == "blocking" for f in findings),
            "evals_hold": any(f["rule"] == "scanner-cannot-run" for f in findings)}


def find_skills(root):
    """The folder itself when it holds a SKILL.md, else every folder below it that does (not below a skill)."""
    found = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in (".git", "__pycache__", "node_modules"))
        if "SKILL.md" in files:
            found.append(dirpath)
            dirs[:] = []
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("--native-tls", action="store_true", help="pass --native-tls to uvx (certificate errors)")
    a = ap.parse_args()
    skills = find_skills(a.skill_dir)
    if not skills:
        sys.exit(f"{a.skill_dir}: no SKILL.md in it or below it")
    cmd = SCANNER[:1] + ["--native-tls"] + SCANNER[1:] if a.native_tls else SCANNER
    if skills == [a.skill_dir]:
        r = scan(a.skill_dir, cmd)
    else:
        rs = [dict(scan(d, cmd), skill=os.path.relpath(d, a.skill_dir).replace("\\", "/")) for d in skills]
        r = {"skills": rs, "blocking": sum(x["blocking"] for x in rs), "evals_hold": any(x["evals_hold"] for x in rs)}
    print(json.dumps(r, indent=2, ensure_ascii=True))
    sys.exit(1 if r["blocking"] else 0)


if __name__ == "__main__":
    main()
