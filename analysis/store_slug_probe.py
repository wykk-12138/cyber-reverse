"""Do the replica's store slugs exist as literals in the original? (R760)

R759 found that seven of ten replica store *display names* have no literal anywhere in the binary. That is not proof the
stores are absent -- a display name can be assembled, or come from a resource -- so the question needs the slug form,
which is what a dispatcher would most likely carry.

For each name this asks two things:
  * is the slug a standalone literal (exact match), which would mean the store is named in code;
  * does the slug appear anywhere as a substring, and in what context, which tells us whether it is a fragment of a URL
    or a path rather than a store identity.

**Why not an existing tool** (AGENTS.md §1.2): this is `search_strings` with two match modes plus a look at surrounding
text. The plugin exposes the search; the added value here is doing it for seven names at once and separating the exact
form from the embedded one.
"""

import json
import os
import re
import subprocess
import sys

IDA = os.path.join(r"D:\projects\cyber-reverse", "analysis", "ida.py")

# replica id -> the literal spellings worth trying
TARGETS = [
    ("superswipe", ["superswipe"]),
    ("yeezysupply", ["yeezysupply", "yeezy.supply"]),
    ("offspring", ["offspring"]),
    ("pocketgames", ["pocketgames", "pocket.games"]),
    ("jbhifi", ["jbhifi", "jb.hifi", "jb-hifi"]),
    ("endclothing", ["endclothing", "end.clothing"]),
    ("notre", ["notre", "notre-shop"]),
]


def call(*args):
    r = subprocess.run([sys.executable, IDA, *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def exact(token):
    d = call("str", "^" + re.escape(token) + "$")
    if not d:
        return []
    return [m for m in d.get("matches", []) if m.get("string") == token]


def embedded(token):
    d = call("str", re.escape(token))
    if not d:
        return []
    return [m for m in d.get("matches", []) if token in m.get("string", "")]


def main():
    print("  %-13s %-10s %-10s %s" % ("replica id", "exact", "embedded", "embedded context (first 3)"))
    print("  " + "-" * 104)
    verdicts = {}
    for rid, tokens in TARGETS:
        ex, em = [], []
        for t in tokens:
            ex.extend(exact(t))
            em.extend(embedded(t))
        # dedupe by address
        ex = {m["addr"]: m for m in ex}
        em = {m["addr"]: m for m in em}
        ctx = []
        for addr, m in list(em.items())[:3]:
            ctx.append(m["string"][:44].replace("\n", " "))
        print("  %-13s %-10d %-10d %s" % (rid, len(ex), len(em), " | ".join(ctx)))
        verdicts[rid] = (len(ex), len(em))

    print()
    named = [r for r, (e, _m) in verdicts.items() if e]
    embedded_only = [r for r, (e, m) in verdicts.items() if not e and m]
    absent = [r for r, (e, m) in verdicts.items() if not e and not m]
    print("  slug exists as a standalone literal : %d  %s" % (len(named), ", ".join(named)))
    print("  slug only appears inside something : %d  %s" % (len(embedded_only), ", ".join(embedded_only)))
    print("  slug appears nowhere               : %d  %s" % (len(absent), ", ".join(absent)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
