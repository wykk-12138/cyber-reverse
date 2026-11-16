"""where_is — before writing something, show where it already exists.

Why this exists
---------------
Four rounds in a row produced work that an existing file already held. R843 rebuilt per-flow step tables that
StoreFlowSteps.cs had carried since R112. R845 counted 108 missing steps that StoreFlow's 165 virtuals already
declared. R846 adjudicated a dual flow that ScapiAppPath.cs had settled in R124. R868 wrote a reflection table whose
job StepActionRunner had been doing for hundreds of rounds, and R869 deleted it again.

Each time the fix was the same shape -- read the right file first -- and each time I discovered the right file by
stumbling onto it. This script makes "the right file" findable on purpose, by grouping every place a name appears into
the four kinds that answer different questions:

    implementation   a file that defines behaviour  — the one R869 should have read
    analysis         a *StepMap / *Steps / *Path file that already worked something out about the image
    test             a file that pins behaviour, and therefore documents what is already guaranteed
    doc              prose that may already state the conclusion

Not in the repository: the image. That is analysis/ida.py, and no script here replaces it.

Usage
    python tools/where_is.py StepDispatch
    python tools/where_is.py --kind impl PopMart
    python tools/where_is.py --all Sequence

Reading only. This never edits anything.
"""

import argparse
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A file is judged by its name and path, never by its content, so the grouping is reproducible and cheap to explain.
ANALYSIS = re.compile(r"(StepMap|Steps|Path|Controllers|ApiFamilies|Endpoints|Witness|Candidate|Parity|Claims)", re.I)
DOC = re.compile(r"\.(md|txt|json)$", re.I)
TEST = re.compile(r"(^|\\|\/)tests(\\|\/)", re.I)


def classify(rel):
    if TEST.search(rel):
        return "test"
    if DOC.search(rel):
        return "doc"
    if ANALYSIS.search(os.path.basename(rel)):
        return "analysis"
    return "impl"


ORDER = ("impl", "analysis", "test", "doc")
HEADING = {
    "impl": "implementation — read this before writing behaviour",
    "analysis": "analysis — something here may already have worked this out",
    "test": "tests — these pin what is already guaranteed",
    "doc": "docs — the conclusion may already be written",
}


def walk():
    for root, dirs, files in os.walk(REPO):
        # .snapshots holds full copies taken by tools/snapshot.py before each mutation; counting them would report
        # every name as living in dozens of places, which is exactly the kind of noise this script exists to remove.
        dirs[:] = [d for d in dirs
                   if d not in (".git", "bin", "obj", ".mutation-backup", "__pycache__", ".snapshots")]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in (".cs", ".md", ".txt", ".json"):
                continue
            p = os.path.join(root, f)
            yield os.path.relpath(p, REPO), p


def main(argv=None):
    ap = argparse.ArgumentParser(description="Show where a name already exists, grouped by what kind of file holds it.")
    ap.add_argument("name", help="identifier to look for")
    ap.add_argument("--kind", choices=ORDER, help="show only one kind")
    ap.add_argument("--all", action="store_true", dest="all_kinds",
                    help="show every hit; by default at most six per kind")
    ap.add_argument("--sub", action="store_true",
                    help="substring match instead of whole-word. Off by default because R884 asked for 'Drop' and "
                         "the substring form returned fifteen files, all of them DropDown and ProxyDrop hits, while "
                         "the type named exactly Drop sat in Checkout.cs and was not among them")
    a = ap.parse_args(argv)

    # Whole-word by default. R884: a substring search for a short type name is dominated by longer names that
    # contain it, so the exact hit is the one most likely to be missed -- the opposite of what a lookup tool is for.
    pat = (re.compile(re.escape(a.name)) if a.sub
           else re.compile(r"\b" + re.escape(a.name) + r"\b"))

    found = {k: [] for k in ORDER}
    for rel, full in walk():
        try:
            text = io.open(full, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        n = len(pat.findall(text))
        if n:
            found[classify(rel)].append((rel, n))

    total = sum(len(v) for v in found.values())
    if total == 0:
        # Absence in the repository is not absence in the image: the replica and the original are different things.
        print("no hit for %r in the repository" % a.name)
        print("  -> if the question is what the IMAGE does, that is analysis/ida.py, not this script")
        return 0

    print("%r appears in %d file(s)\n" % (a.name, total))
    for k in ORDER:
        if a.kind and k != a.kind:
            continue
        rows = sorted(found[k], key=lambda r: (-r[1], r[0]))
        if not rows:
            continue
        print("%s (%d)" % (HEADING[k], len(rows)))
        for rel, n in (rows if a.all_kinds else rows[:6]):
            print("    %-58s %3d" % (rel, n))
        if not a.all_kinds and len(rows) > 6:
            print("    ... %d more (--all)" % (len(rows) - 6))
        print()

    impl = len(found["impl"])
    if a.kind in (None, "impl") and impl:
        print("start with implementation: %d file(s) define behaviour under this name" % impl)
    return 0


if __name__ == "__main__":
    sys.exit(main())
