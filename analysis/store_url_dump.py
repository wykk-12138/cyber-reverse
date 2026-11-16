"""Dump every URL-shaped string per store, without classifying first. (R768)

R767's probe printed "NO-URLS" for five stores. That label was wrong and it was mine: the verdict was expressed as

    "CHECKOUT" if checkout-hits else ("OTHER-SHAPE" if other-hits else "NO-URLS")

so a store with URLs that matched neither keyword fell through to "NO-URLS", which reads as "the image names no URL
for this store" -- a much stronger claim than the code had checked. yeezysupply has had
`https://www.yeezysupply.com` in the pool since R757, so the label was demonstrably false.

Same shape as R764's "class not found": the diagnostic named the wrong cause, and a wrong cause is worse than none
because it sends the next reader somewhere else. So this dumps first and classifies later, and it separates three
things the old label conflated:

    NO-STRINGS   the domain does not appear at all
    STRINGS      it appears, but nothing URL-shaped
    URLS         it appears with URLs; the classification is reported, not decided

**Why not an existing tool** (AGENTS.md §1.2): `search_strings` per domain. The only thing added is not conflating
"no keyword match" with "no URL", which is what the previous script did.
"""

import json
import os
import re
import subprocess
import sys

IDA = os.path.join(r"D:\projects\cyber-reverse", "analysis", "ida.py")

STORES = [
    ("bstn", ["bstn.com", "bstn"]),
    ("fanatics", ["fanatics.com"]),
    ("offspring", ["offspring.co.uk", "offspring.com"]),
    ("warhammer", ["warhammer.com", "games-workshop.com"]),
    ("yeezysupply", ["yeezysupply.com"]),
]

URLISH = re.compile(r"(https?://\S+|^/\S*|[\w.-]+\.(com|co\.uk|net|io)/\S*)")


def call(*args):
    r = subprocess.run([sys.executable, IDA, *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def main():
    for name, tokens in STORES:
        seen, strings, urls = set(), [], []
        for tok in tokens:
            d = call("str", re.escape(tok))
            for m in (d or {}).get("matches", []):
                if m["addr"] in seen:
                    continue
                seen.add(m["addr"])
                s = m["string"]
                if tok not in s:
                    continue
                strings.append(s)
                for hit in URLISH.findall(s):
                    u = hit[0] if isinstance(hit, tuple) else hit
                    if len(u) > 8:
                        urls.append(u)
        state = "NO-STRINGS" if not strings else ("URLS" if urls else "STRINGS")
        print("  %-12s %-11s strings=%-3d urls=%d" % (name, state, len(strings), len(urls)))
        for u in sorted(set(urls))[:10]:
            print("      %s" % u[:100])
        if state == "STRINGS":
            for s in strings[:4]:
                print("      (no url) %r" % s[:84])
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
