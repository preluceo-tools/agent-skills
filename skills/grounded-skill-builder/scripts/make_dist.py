"""Zip a finished skill folder for distribution, after checking it for paths from this machine.

Refuses to build when any file contains the home folder, the user name, or an absolute
Windows drive path, because those read as instructions on someone else's machine.

usage: python make_dist.py <skill folder> <dist folder> --version 1.0.0
writes <dist folder>/<skill name>-<version>.zip with the skill folder as its single top-level entry

usage: python make_dist.py <skill folder> --check
only runs the leak check: prints each leaking line, exit code 1 when any; writes nothing
"""
import argparse, getpass, os, re, sys, zipfile


def leaks(root):
    home = os.path.expanduser("~")
    needles = {home, home.replace("\\", "/"), getpass.getuser()}
    drive = re.compile(r"\b[A-Za-z]:[\\/](?![\\/])")
    for dirpath, _, files in os.walk(root):
        for f in files:
            p = os.path.join(dirpath, f)
            try:
                text = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if any(n and n in line for n in needles) or drive.search(line):
                    yield os.path.relpath(p, root), i, line.strip()[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("dist_dir", nargs="?")
    ap.add_argument("--version")
    ap.add_argument("--check", action="store_true", help="only check for leaks; build no zip")
    a = ap.parse_args()
    if not a.check and not (a.dist_dir and a.version):
        ap.error("give <dist folder> and --version, or --check")
    found = list(leaks(a.skill_dir))
    for rel, i, line in found:
        print(f"{rel}:{i}: {line}")
    if found:
        sys.exit(f"{len(found)} line(s) name paths or the user of this machine; replace them with placeholders first.")
    if a.check:
        print("no paths or user name of this machine found")
        return
    name = os.path.basename(os.path.realpath(a.skill_dir))
    os.makedirs(a.dist_dir, exist_ok=True)
    out = os.path.join(a.dist_dir, f"{name}-{a.version}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(a.skill_dir):
            for f in sorted(files):
                p = os.path.join(dirpath, f)
                z.write(p, os.path.join(name, os.path.relpath(p, a.skill_dir)))
    print(f"{out}  {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
