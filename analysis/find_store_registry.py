"""Locate the original's store registry by intersecting the functions that name stores. (R759)

R757's substring map cannot answer "which stores does the original dispatch", and R759 found that following a store's
base URL leads into that module's async state machine rather than any table. The registry should instead be the one
function that mentions many store names at once.

Method: take several store display names that are unlikely to occur as ordinary English, resolve each literal, ask for
cross-references at the frozen-string object header (chars - 12, the R720 rule -- asking at the characters returns
nothing because NativeAOT code addresses the header), and intersect the containing functions. A function that names
several stores is either the registry or the catalogue that feeds it.

**Why not an existing tool** (AGENTS.md §1.2): this needs the idb's own string table and xref graph, which is exactly
what the IDA plugin exposes; `search_strings` and `xrefs_to` are the tools, and the only thing added here is the -12
adjustment and the intersection.
"""

import json
import os
import re
import subprocess
import sys

IDA = os.path.join(r"D:\projects\cyber-reverse", "analysis", "ida.py")

# Distinctive store names. Chosen to be unlikely as ordinary words, and to span different platforms.
NAMES = [
    "Footpatrol",
    "Superswipe",
    "Warhammer",
    "Pocket Games",
    "JB Hi-Fi",
    "Yeezy Supply",
    "END.",
    "Notre",
    "John Lewis",
    "Offspring",
]


def call(*args):
    r = subprocess.run([sys.executable, IDA, *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def literal_addrs(name):
    """Addresses of exact-match literals for this name."""
    d = call("str", "^" + re.escape(name) + "$")
    if not d:
        return []
    return [m["addr"] for m in d.get("matches", []) if m.get("string") == name]


def referencing_functions(addr):
    base = int(addr, 16)
    header = "0x%x" % (base - 12)
    d = call("xrefs", header)
    if not d:
        return []
    out = []
    for row in d:
        for x in row.get("xrefs", []):
            fn = x.get("fn") or {}
            if fn.get("addr"):
                out.append((fn["addr"], fn.get("name", "?"), int(fn.get("size", "0"), 16)))
    return out


def main():
    per_name = {}
    for name in NAMES:
        addrs = literal_addrs(name)
        fns = set()
        for a in addrs:
            for fa, fn, sz in referencing_functions(a):
                fns.add((fa, fn, sz))
        per_name[name] = fns
        print("  %-14s literals=%d  functions=%s" % (
            name, len(addrs),
            ", ".join("%s(%d B)" % (fn, sz) for _fa, fn, sz in sorted(fns)) or "-- none --"))

    print()
    holders = [set(fa for fa, _n, _s in fns) for fns in per_name.values() if fns]
    if not holders:
        print("  no functions found; nothing to intersect")
        return 0
    common = set.intersection(*holders)
    print("  functions naming ALL of the resolved stores: %d" % len(common))
    for fa in sorted(common):
        meta = next((fn, sz) for fns in per_name.values() for a, fn, sz in fns if a == fa)
        print("    0x%s  %s  %d B" % (fa[2:] if fa.startswith("0x") else fa, meta[0], meta[1]))

    # also report the widest holders, which is the nearest thing to a registry if the intersection is empty
    counts = {}
    for fns in per_name.values():
        for fa, fn, sz in fns:
            counts.setdefault((fa, fn, sz), set()).add(fa)
    ranked = sorted(((len(v), k) for k, v in counts.items()), reverse=True)
    print()
    print("  widest holders (candidate registry if the intersection is empty):")
    for n, (fa, fn, sz) in ranked[:6]:
        names_here = [name for name, fns in per_name.items() if any(a == fa for a, _f, _s in fns)]
        print("    %-12s %d B  names: %s" % (fn, sz, ", ".join(names_here)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
