"""Every numbered stage family in the image, which is a flow map that needs no type mapping.

R1053 found that PayPal 3DS carries nine staged strings -- (1), (2), (2.1), (3) through (8) -- and that the 2.1 meant
nine observable stages rather than eight. That is ordering evidence sitting in the string pool, and it does not require
joining names to addresses, which R1072 showed is a project.

So the question this answers is: which flows in the image announce their steps as a numbered family, and in what order.
A family with contiguous ordinals is a sequence; a family missing one is either a conditional branch or a gap in the
pool window, and the difference is checkable by looking for the missing number directly.

R1067's cap applies, so queries are sharded by first letter of the prefix where a prefix is needed.

Run: python analysis/stage_families.py
"""

import json
import re
import subprocess
import sys
from collections import defaultdict

ROOT = r"D:\projects\cyber-reverse"
CAP = 500

# R1073: no end anchor. The pool shares string tails, so "Solving PayPal 3DS (1)" comes back without its closing
# parenthesis -- the ")" is shared with a neighbouring entry. Anchoring at $ made every such string fail to match and
# the tool reported zero families while the strings were plainly there.
FAMILY = re.compile(r"^(.*?)\s*\((\d+(?:\.\d+)?)\)?")


def probe(pattern, limit=CAP):
    p = subprocess.run([sys.executable, "analysis/ida.py", "str", pattern, "--limit", str(limit)],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    try:
        return json.loads((p.stdout or "").strip())
    except Exception:
        m = re.search(r"\{.*\}", p.stdout or "", re.S)
        return json.loads(m.group(0)) if m else {"n": 0, "matches": []}


def main():
    control = probe("kpsdk").get("n", -1)

    families = defaultdict(list)
    saturated = []
    # Shard on the parenthesised digit, which is the part every family has in common.
    for d in "123456789":
        pattern = r"\(%s" % d
        got = probe(pattern)
        hits = got.get("matches", [])
        if len(hits) >= CAP:
            saturated.append(pattern)
        for hit in hits:
            s = hit.get("string", "")
            m = FAMILY.match(s.strip())
            if m:
                families[m.group(1).strip()].append(m.group(2))

    print("  control kpsdk n=%d" % control)
    print("  shards saturated: %d %s" % (len(saturated), ", ".join(saturated)))
    # R1073: a family is a readable phrase with at least two ordinals. Without both filters the run produced 35
    # "families" of which 33 were byte noise -- a lone "0", control characters, a truncated error message -- because
    # any byte run ending in "(" plus a digit matches once the end anchor is gone. A single-ordinal prefix is not a
    # stage family either; it is one string that happens to contain a number in brackets.
    def readable(name):
        return (len(name) >= 6 and " " in name
                and all(32 <= ord(c) < 127 for c in name))
    real = {k: v for k, v in families.items() if readable(k) and len(set(v)) >= 2}
    print("  families with numbered stages: %d (readable and multi-stage: %d)" % (len(families), len(real)))
    print()
    for name in sorted(real, key=lambda k: (-len(real[k]), k)):
        stages = real[name]
        # numeric sort, with sub-stages between their parents
        def key(s):
            return tuple(int(p) for p in s.split("."))
        ordered = sorted(set(stages), key=key)
        print("  %-46s %2d stages: %s" % (name[:46], len(ordered), " ".join(ordered)))
    print()
    if saturated:
        print("  NOTE: %d shard(s) hit the 500 cap, so this list is a sample for those digits." % len(saturated))
    return 0


if __name__ == "__main__":
    sys.exit(main())
