"""Fifth metric: the original's binding-descriptor table vs the XAML-derived table.

WHY THIS EXISTS (AGENTS.md §1.2 requires the reason be stated):
The other binding metrics all take `docs/xaml_bindings.json` as "what the original binds". R463/R464 proved
that table is a **strict subset** of the descriptors the original actually declares in its string pool
(`analysis/binding_descriptors.py`): 819 members shared, 132 more that XAML never mentions, and zero XAML
members missing from the descriptors. So every metric built on the XAML table under-reports by that margin,
and there was no number in `docs/METRICS.md` saying so.

This prints the comparison as a one-line summary so `metrics_report.py` can carry it. It does **not** run
IDA — descriptor extraction is a slow, IDB-dependent step; this reads the TSV that step already wrote and
fails loudly if the TSV is missing (rather than silently reporting zeros).

Reproduce:
    cd replica
    python tools/descriptor_report.py          # after: python analysis/binding_descriptors.py
"""

import io
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TSV = os.path.abspath(os.path.join(ROOT, "..", "analysis", "binding_descriptors.tsv"))
BINDS = os.path.join(ROOT, "docs", "xaml_bindings.json")


def main():
    if not os.path.exists(TSV):
        print("missing %s" % TSV)
        print("run first: cd ..; python analysis/binding_descriptors.py")
        return 2

    rows = []
    for line in io.open(TSV, encoding="utf-8").read().splitlines()[1:]:
        if not line.strip():
            continue
        decl, _asm, member, accessor = line.split("\t")
        rows.append((decl, member, accessor))

    binds = json.load(io.open(BINDS, encoding="utf-8"))
    xaml = {(typ, member) for typ, members in binds.items() for member in members}
    desc = {(decl, member) for decl, member, _acc in rows}

    types = {decl for decl, _m, _a in rows}
    setters = {(decl, member) for decl, member, acc in rows if acc == "Setter"}

    only_desc = desc - xaml
    only_xaml = xaml - desc

    print("descriptor entries      : %d" % len(desc))
    print("descriptor types        : %d" % len(types))
    print("entries with a setter   : %d" % len(setters))
    print("xaml table entries      : %d" % len(xaml))
    print("shared                  : %d" % len(desc & xaml))
    print("only in descriptors     : %d" % len(only_desc))
    print("only in xaml table      : %d" % len(only_xaml))
    if only_xaml:
        print("  (only-in-xaml is expected to be 0 while the XAML table stays a subset)")
        for typ, member in sorted(only_xaml)[:10]:
            print("    %s . %s" % (typ, member))
    return 0


if __name__ == "__main__":
    sys.exit(main())
