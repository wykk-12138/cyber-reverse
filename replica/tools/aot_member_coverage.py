r"""Product-level member coverage: XAML binding table vs. the AOT artifact's own symbols.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
Every existing metric in this repository reads SOURCE (`bind_diff.py`, `bind_scope.py`,
`shape_audit.py`). None of them can answer "did this member survive the linker". NativeAOT is
free to inline, trim or drop any member that nothing reachable calls, so a member can pass every
source-level check and still be absent from the shipped product -- which is exactly the class of
difference the 1:1 claim is about. `rea` cannot answer it either: its native comparison tools need
a provider this host does not have (IDA MCP's attached profile requires legacy tool names), and its
.NET tools need CLR metadata that an AOT image does not carry.

Input is the symbol inventory IDA produced for the published AOT image (see the command in
README of this file's header block below), so both sides are observations, not inferences:

    left  : replica/docs/xaml_bindings.json          (174 types / 819 members, from the original)
    right : analysis/replica_funcs.txt                (address<TAB>size<TAB>name, one per function;
                                                       exported by `python analysis/func_compare.py`)

Reproduce:
    cd D:\projects\cyber-reverse && python analysis/func_compare.py --export-only
    cd replica && python tools/aot_member_coverage.py
    python tools/aot_member_coverage.py --missing-only
    python tools/aot_member_coverage.py --type MonitorView

What the answer means:
    method   -> a symbol ending in <Type>__<Member> exists
    property -> a symbol ending in <Type>__get_<Member> (or __set_) exists
    absent   -> no symbol carries that member; the product has no body for it (trimmed, inlined,
                or never implemented). This is NOT proof the original behaviour is missing --
                an inlined property still returns a value -- it is proof we cannot see the member
                as its own function in the product.

Authority: observed (symbols read out of the published image by IDA). Absence is a statement about
this build only: a different RID/configuration can produce a different tree.
"""

import io
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BINDS = os.path.join(ROOT, "docs", "xaml_bindings.json")
SYMBOLS = os.path.abspath(os.path.join(ROOT, "..", "analysis", "replica_funcs.txt"))


def load_symbols(path):
    if not os.path.exists(path):
        raise SystemExit(
            "missing symbol inventory: %s\n"
            "produce it first:  python analysis/func_compare.py --export-only\n"
            "(that exports original_funcs.txt and replica_funcs.txt from the two live IDA instances)"
            % path)
    names = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3 and parts[2]:
            names.append(parts[2])
    return names


def marker(full_name):
    """Class name only: `A.B.C.D` -> `D`.

    Short-name matching is deliberate and matches `analysis/func_compare.py`. The replica renames
    types freely (AGENTS.md allows different naming), so a full-namespace match reports "absent" for
    a member that is simply on a renamed type (`SettingsView` -> `Settings_SettingsShell`). Using the
    short name keeps this tool and func_compare.py on ONE number instead of two.
    """
    return full_name.split(".")[-1]


def classify(names, type_full, member):
    base = marker(type_full)
    for suffix, kind in (("__get_" + member, "property-get"),
                         ("__set_" + member, "property-set"),
                         ("__" + member, "method")):
        needle = "_" + base + suffix
        for name in names:
            if name.endswith(needle):
                return kind
    return None


def main(argv):
    missing_only = "--missing-only" in argv
    only_type = None
    if "--type" in argv:
        only_type = argv[argv.index("--type") + 1].lower()

    binds = json.load(io.open(BINDS, encoding="utf-8"))
    names = load_symbols(SYMBOLS)

    present_types = 0
    total_members = 0
    covered = 0
    rows = []
    for full, members in sorted(binds.items()):
        short = full.split(".")[-1]
        if only_type and only_type not in short.lower():
            continue
        hits, misses = {}, []
        for member in sorted(members):
            total_members += 1
            kind = classify(names, full, member)
            if kind:
                covered += 1
                hits[member] = kind
            else:
                misses.append(member)
        if hits:
            present_types += 1
        rows.append((short, full, hits, misses))

    print("product-level coverage: xaml binding table vs. published AOT image")
    print("  symbols in image : %d  (%s)" % (len(names), SYMBOLS))
    print("  binding types    : %d" % len(binds))
    print("  binding members  : %d" % total_members)
    if total_members:
        print("  members with a body in the product : %d (%.1f%%)"
              % (covered, 100.0 * covered / total_members))
    print("  types with at least one member present : %d" % present_types)
    print()

    for short, full, hits, misses in rows:
        if missing_only and not misses:
            continue
        if not missing_only and not misses:
            continue
        print("  %-30s %s" % (short, "" if hits else "(no member found)"))
        for member in misses:
            print("      absent  %s" % member)
        if hits and ("--type" in argv or not missing_only):
            kinds = {}
            for member, kind in hits.items():
                kinds.setdefault(kind, []).append(member)
            for kind, group in sorted(kinds.items()):
                print("      %-12s %s" % (kind, ", ".join(group)))

    gap_types = [r for r in rows if r[3]]
    print()
    print("types with at least one absent member:", len(gap_types))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
