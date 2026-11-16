"""Enumerate the original's per-store configuration records. (R761)

Criterion (f) needs the original's store list taken from the binary. Three approaches failed or misled first:

  * R757 counted substrings in the source pool -- a map, and it conflated step names with stores.
  * R759 followed a store's base URL and landed in that module's async state machine.
  * R759 intersected functions naming stores and got a 687 KB IDA blob, not a function.

R760/761 found why: the original keeps store metadata as **data records**, not as code. Each record is a run of
packed `FieldName` + value pairs, for example

    CaptchaOrigin<https://captcha.superswipe.com
    ProgressApi:https://status.superswipe.com
    EntryUrlDhttps://enter.superswipe.com/enter
    ClickTrackerUrl>https://clicks.superswipe.com/c"SubdomainAlphabetHabcdefghijklmnopqrstuvwxyz0123456789

where the single character between the name and the value is a length or separator byte. Records are contiguous, so
grouping the matches by address locality reassembles each store's field set.

**Why not an existing tool** (AGENTS.md §1.2): this is `search_strings` plus grouping. The plugin does the search; the
part that is missing everywhere is the observation that store metadata lives in packed data rather than in code, and
the grouping that follows from it.
"""

import json
import os
import re
import subprocess
import sys

IDA = os.path.join(r"D:\projects\cyber-reverse", "analysis", "ida.py")

# A capitalised field name (4..26 chars), then one separator byte, then a value that looks like a URL, a path, a
# token, or a run of lowercase/digits.
RECORD = re.compile(
    r"^([A-Z][A-Za-z]{3,25})"           # field name
    r"[\x00-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]"   # one separator byte
    r"(https?://\S+|_[A-Za-z_]+|[a-z0-9]{8,}|[A-Za-z0-9\.\-/:_]{4,})"  # value
)

# How far apart two matches can be and still belong to the same record.
LOCALITY = 0x400


def call(*args):
    r = subprocess.run([sys.executable, IDA, *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def collect():
    """Ask for any string containing a capitalised name followed by a URL, then keep the ones that parse."""
    d = call("str", r"[A-Z][A-Za-z]{3,25}[\x00-\x2f\x3a-\x40]https?://")
    rows = []
    for m in (d or {}).get("matches", []):
        s = m.get("string", "")
        hit = RECORD.match(s)
        if not hit:
            continue
        rows.append({"addr": int(m["addr"], 16), "field": hit.group(1), "value": hit.group(2)[:96], "raw": s})
    rows.sort(key=lambda r: r["addr"])
    return rows


def group(rows):
    groups, current = [], []
    for r in rows:
        if current and r["addr"] - current[-1]["addr"] > LOCALITY:
            groups.append(current)
            current = []
        current.append(r)
    if current:
        groups.append(current)
    return groups


def main():
    rows = collect()
    print("  field-value pairs: %d" % len(rows))
    if not rows:
        print("  nothing matched; the pattern or the search needs revisiting")
        return 0
    groups = group(rows)
    print("  records (by address locality, gap <= 0x%x): %d" % (LOCALITY, len(groups)))
    print()
    for g in groups:
        fields = [r["field"] for r in g]
        print("  0x%x .. +%d  fields=%d" % (g[0]["addr"], g[-1]["addr"] - g[0]["addr"], len(g)))
        for r in g:
            print("    %-22s %s" % (r["field"], r["value"]))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
