"""Does `Setter` mean "has a set accessor" or "the binding writes back"? (R717)

R716 left the question open: Setter is the only descriptor dimension that varies (77.9%), and two readings explain it --
(a) the member declares a setter, (b) the binding is two-way.

**Test**: split the 819 by descriptor (G+S vs G-only) and report, per group, how often the string pool carries a
`set_<Member>` accessor name.

    G+S markedly higher  -> Setter tracks the accessor, i.e. reading (a)
    both groups similar  -> Setter tracks the binding mode, i.e. reading (b)

**Known limitation, stated before measuring**: `set_X` strings are not type-qualified (R715), so a hit may belong to a
different type that happens to share the name. That noise applies to both groups in proportion to how common the name is,
so the comparison between groups survives even though an individual row does not.
"""

import io
import json
import re
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import c10_split as S

STRINGS = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
PAT = re.compile(r"(Cybersole[\w.`]*?),([\w.`]+?)!(Getter|Setter|Property)")
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def index_kinds():
    out = {}
    with io.open(STRINGS, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            for m in PAT.finditer(line):
                if not m.group(1).startswith("Cybersole."):
                    continue
                out.setdefault((m.group(1).split(".")[-1], m.group(2).split(".")[-1]), set()).add(m.group(3))
    return out


def index_accessors():
    """set of names N for which a `set_N` string appears anywhere in the pool."""
    setter_names, getter_names = set(), set()
    with io.open(STRINGS, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "set_" not in line and "get_" not in line:
                continue
            for token in WORD.findall(line):
                if token.startswith("set_") and len(token) > 4:
                    setter_names.add(token[4:])
                elif token.startswith("get_") and len(token) > 4:
                    getter_names.add(token[4:])
    return getter_names, setter_names


def main():
    kinds = index_kinds()
    getters, setters = index_accessors()
    print("accessor names in the pool: get_=%d  set_=%d" % (len(getters), len(setters)))
    print()

    bindings = json.load(io.open(S.BINDINGS, encoding="utf-8"))
    groups = {"G+S": [0, 0], "G only": [0, 0]}   # [members, with set_ accessor]
    examples = []

    for full_type, members in bindings.items():
        simple, _r = S.resolve(full_type, S.renames())
        for member in members:
            keys = [k for k in ((simple, member), (simple.split("`")[0], member)) if k in kinds]
            ks = set().union(*[kinds[k] for k in keys]) if keys else set()
            if "Setter" in ks:
                g = "G+S"
            elif "Getter" in ks:
                g = "G only"
            else:
                continue
            groups[g][0] += 1
            if member in setters:
                groups[g][1] += 1
                if g == "G only" and len(examples) < 8:
                    examples.append((simple, member))

    print("%-8s %8s %10s %10s" % ("group", "members", "has set_", "share"))
    for g, (n, hits) in groups.items():
        share = (100.0 * hits / n) if n else 0.0
        print("%-8s %8d %10d %9.1f%%" % (g, n, hits, share))
    print()
    if examples:
        print("G-only members that nevertheless have a set_ string (noise or a real setter):")
        for t, m in examples:
            print("  %-24s %s" % (t, m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
