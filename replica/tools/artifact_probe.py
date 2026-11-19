#!/usr/bin/env python3
"""Probe an artifact for strings, and record which artifact answered.

Why this exists (AGENTS.md §1 rule 2): no public tool in seep-reverse-lab or rea answers
"is this literal in this binary, and which binary was it". `where_is.py` answers for the
replica source, `analysis/ida.py str` answers for the original's database, and `pe_triage.py`
reports layout. The gap is small and specific: a reading that carries the identity of the
artifact it came from.

R1006 is the reason. Readings taken across three publishes were treated as one timeline, so a
single wrong reading became a fact that carried an argument -- `StoreFlowRunner` was recorded
present in R1002 and absent in R1006 with the function count unchanged, and nothing written down
could say which reading was wrong. The fix is not a better probe, it is a probe that cannot
answer without saying which file it read.

Usage:
    python tools/artifact_probe.py --strings a b c
    python tools/artifact_probe.py --strings-file analysis/probes.txt --exe .publish-aot/Cybersole.Ui.exe
    python tools/artifact_probe.py --strings StoreFlowRunner --json   # machine-readable

Every run appends one record to analysis/ARTIFACT_PROBES.json, keyed by the artifact's sha256,
so two readings of the same literal can be compared only when they agree on that digest. A
mismatch between records with different digests is a change in the build; a mismatch between
records with the same digest is a defect in this tool or in the reading, and either way it is
visible instead of being averaged away.
"""

import argparse
import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_EXE = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")
RECORD = os.path.join(ROOT, "..", "analysis", "ARTIFACT_PROBES.json")

# String literals in the replica are UTF-16LE; reflection metadata and some payloads are UTF-8.
# R967 established the split, and checking only one encoding has produced a confident "absent"
# more than once, so both are reported rather than merged.
ENCODINGS = (("utf-16-le", "utf-16-le"), ("utf-8", "utf-8"))


def identity(path):
    """The artifact's identity: digest, size, mtime. A reading without these is not a reading."""
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        while True:
            block = f.read(1 << 20)
            if not block:
                break
            h.update(block)
            size += len(block)
    st = os.stat(path)
    # R1182: relpath raises ValueError when the artifact sits on another drive than the repository, and two
    # guards that passed a temporary file from %TEMP% hit exactly that - the tool crashed instead of reading.
    try:
        rel = os.path.relpath(path, ROOT)
    except ValueError:
        rel = path
    return {
        "path": rel.replace("\\", "/"),
        "sha256": h.hexdigest(),
        "bytes": size,
        "mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime)),
    }


def probe(path, needles):
    blob = open(path, "rb").read()
    rows = []
    for needle in needles:
        counts = {}
        for enc, _ in ENCODINGS:
            counts[enc] = blob.count(needle.encode(enc))
        rows.append({
            "string": needle,
            "utf-16-le": counts["utf-16-le"],
            "utf-8": counts["utf-8"],
            # present when either encoding carries it; a count of zero in both is the only absence
            "present": counts["utf-16-le"] > 0 or counts["utf-8"] > 0,
        })
    return rows


def previous(record, digest):
    """Earlier readings against the same digest, so a disagreement can be seen rather than assumed."""
    same, other = [], []
    for run in record.get("runs", []):
        for run_id in run.get("artifacts", []):
            if run.get("artifact", {}).get("sha256") == digest:
                same.append(run)
            else:
                other.append(run)
    return same, other


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=DEFAULT_EXE)
    ap.add_argument("--strings", nargs="*", default=None)
    ap.add_argument("--strings-file", default=None)
    ap.add_argument("--json", action="store_true", help="print the record instead of a table")
    ap.add_argument("--no-record", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.exe):
        print("no artifact at %s" % args.exe)
        return 2

    needles = list(args.strings or [])
    if args.strings_file:
        # R1180: utf-8-sig, because a probe file written by `Set-Content -Encoding utf8` starts with a BOM,
        # and the BOM then rides along on the FIRST needle only - which made the first row of every table a
        # false absence. The command-line route never showed it, so the defect hid in exactly the rows that
        # were quoted as evidence.
        for line in io.open(args.strings_file, encoding="utf-8-sig"):
            line = line.strip()
            if line and not line.startswith("#"):
                needles.append(line)
    if not needles:
        print("no strings to probe")
        return 2

    art = identity(args.exe)
    rows = probe(args.exe, needles)

    entry = {
        "artifact": art,
        "strings": rows,
        "present": [r["string"] for r in rows if r["present"]],
        "absent": [r["string"] for r in rows if not r["present"]],
    }

    record = {"runs": []}
    if os.path.exists(RECORD):
        try:
            record = json.load(io.open(RECORD, encoding="utf-8"))
        except Exception:
            record = {"runs": []}
    record.setdefault("runs", []).append(entry)
    # keep the file bounded; the point is comparison with the recent past, not an archive
    record["runs"] = record["runs"][-200:]
    if not args.no_record:
        io.open(RECORD, "w", encoding="utf-8", newline="\n").write(
            json.dumps(record, indent=1, ensure_ascii=False) + "\n")

    if args.json:
        print(json.dumps(entry, indent=1, ensure_ascii=False))
        return 0

    print("artifact  %s" % art["path"])
    print("sha256    %s" % art["sha256"])
    print("bytes     %s   mtime %s" % (art["bytes"], art["mtime"]))
    print()
    print("  %-34s %10s %10s  %s" % ("string", "utf-16-le", "utf-8", "present"))
    for r in rows:
        print("  %-34s %10d %10d  %s" % (r["string"][:34], r["utf-16-le"], r["utf-8"],
                                         "yes" if r["present"] else "no"))
    # R1176: a "no" is not evidence of absence. Measured on the current artifact: "Cart-AddProduct" and
    # "Checkout-Begin" are absent even though DemandwareFlow uses both at runtime (posts at line 279, gets
    # at 425), because StepActionRunner dispatches step bodies by reflection and the AOT trimmer cannot see
    # through it, so those bodies - and their literals - are dropped. Only a "yes" carries information.
    if any(not r["present"] for r in rows):
        print()
        print("  A 'no' means the literal is not retained, not that the code is dead: reflectively")
        print("  dispatched step bodies are trimmed whole, so their literals disappear with them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
