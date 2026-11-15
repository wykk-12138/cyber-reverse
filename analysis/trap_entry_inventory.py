"""Inventory which recorded traps have an operational entry point. (R697)

**Why this exists** (project convention §1.2): this counts cross-references between local text files. No reverse
engineering tool applies; the IDA instance is not consulted.

**Why now**: R695 found that the readiness trap was documented at R433, had a criterion at R613, and was still repeated
at R694. R696 fixed that one case by moving the criterion into the code that takes the measurement. That raises the
question this script answers: **how many other traps live only in a report?**

**Criterion, fixed before measuring** -- a trap "has an operational entry point" when at least one of:
  1. a script's **header** (first 45 lines, where §1.2 requires the reason to be stated) mentions its round id;
  2. a test file mentions its round id;
  3. the operations manual (`docs/IDA_STARTUP_CHECKLIST.md` or `docs/DEVIATIONS.md`) mentions it.

Otherwise it is "report only". Round ids are read from the section headings in `docs/BLOCKERS.md`.
"""

import io
import os
import re
import sys

ROOT = r"D:\projects\cyber-reverse"
BLOCKERS = os.path.join(ROOT, "docs", "BLOCKERS.md")
MANUALS = [
    os.path.join(ROOT, "docs", "IDA_STARTUP_CHECKLIST.md"),
    os.path.join(ROOT, "docs", "DEVIATIONS.md"),
]

HEADER_LINES = 45
ROUND = re.compile(r"R(\d{3})")


def traps():
    """[(section_title, {round_ids})] from BLOCKERS.md level-2 headings."""
    text = io.open(BLOCKERS, encoding="utf-8").read()
    blocks = re.split(r"\n## ", text)
    out = []
    for b in blocks[1:]:
        title = b.splitlines()[0].strip()
        body = b
        ids = sorted(set(ROUND.findall(body)))
        if ids:
            out.append((title, ids, body))
    return out


def collect_sources():
    """(path, kind, text) for scripts' headers, tests, and manuals."""
    out = []
    for sub in ("analysis", os.path.join("replica", "tools")):
        d = os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".py"):
                continue
            p = os.path.join(d, f)
            try:
                lines = io.open(p, encoding="utf-8", errors="replace").read().splitlines()[:HEADER_LINES]
            except OSError:
                continue
            out.append((p, "script-header", "\n".join(lines)))
    tests = os.path.join(ROOT, "replica", "tests")
    for dp, _dn, fn in os.walk(tests):
        if "obj" in dp or "bin" in dp:
            continue
        for f in fn:
            if f.endswith(".cs"):
                p = os.path.join(dp, f)
                try:
                    out.append((p, "test", io.open(p, encoding="utf-8", errors="replace").read()))
                except OSError:
                    pass
    for p in MANUALS:
        if os.path.exists(p):
            out.append((p, "manual", io.open(p, encoding="utf-8", errors="replace").read()))
    return out


def main():
    rows = traps()
    srcs = collect_sources()
    print("traps (BLOCKERS.md sections carrying round ids): %d" % len(rows))
    print("sources scanned: scripts=%d tests=%d manuals=%d"
          % (sum(1 for s in srcs if s[1] == "script-header"),
             sum(1 for s in srcs if s[1] == "test"),
             sum(1 for s in srcs if s[1] == "manual")))
    print()

    with_entry, report_only = [], []
    for title, ids, _body in rows:
        hits = []
        for rid in ids:
            token = "R" + rid
            for path, kind, text in srcs:
                if token in text:
                    hits.append((kind, os.path.basename(path), token))
        if hits:
            with_entry.append((title, ids, hits))
        else:
            report_only.append((title, ids))

    print("have an operational entry point : %d" % len(with_entry))
    print("report only                     : %d" % len(report_only))
    print()
    print("=== report only (the population at risk of an R694-style repeat) ===")
    for title, ids in report_only:
        print("  R%-12s %s" % ("/".join(ids), title[:96]))
    print()
    print("=== entry kinds for the ones that have one ===")
    kinds = {}
    for _t, _i, hits in with_entry:
        for kind, _f, _tok in hits:
            kinds[kind] = kinds.get(kind, 0) + 1
    for k, v in sorted(kinds.items(), key=lambda x: -x[1]):
        print("  %-14s %d" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
