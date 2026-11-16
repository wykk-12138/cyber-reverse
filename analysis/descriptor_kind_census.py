"""How often does each descriptor kind occur across the 819 members? (R716b)

`descriptor_kinds.py` showed every member of four views carrying `Getter/Property/Setter`, including members already
implemented here as ICommand. If `!Property` is near-universal, the kind field cannot separate anything -- which extends
R714's finding from "78% are Getter+Setter" to "the kinds are emitted for every binding regardless of shape".

**Criterion**: report the fraction of the 819 members carrying each kind and each combination. A kind present on
essentially every member is background, not a signal.
"""

import io
import json
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import c10_split as S

STRINGS = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
import re

PAT = re.compile(r"(Cybersole[\w.`]*?),([\w.`]+?)!(Getter|Setter|Property)")


def index_all():
    out = {}
    with io.open(STRINGS, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            for m in PAT.finditer(line):
                typ, owner, kind = m.group(1), m.group(2), m.group(3)
                if not typ.startswith("Cybersole."):
                    continue
                out.setdefault((typ.split(".")[-1], owner.split(".")[-1]), set()).add(kind)
    return out


def main():
    idx = index_all()
    bindings = json.load(io.open(S.BINDINGS, encoding="utf-8"))
    total = 0
    combos = {}
    per_kind = {"Getter": 0, "Setter": 0, "Property": 0}
    for full_type, members in bindings.items():
        simple, _res = S.resolve(full_type, S.renames())
        for member in members:
            total += 1
            keys = [k for k in ((simple, member), (simple.split("`")[0], member)) if k in idx]
            kinds = set().union(*[idx[k] for k in keys]) if keys else set()
            combos[frozenset(kinds)] = combos.get(frozenset(kinds), 0) + 1
            for k in kinds:
                per_kind[k] += 1

    print("binding members: %d" % total)
    for k, n in per_kind.items():
        print("  carries %-9s %4d  (%.1f%%)" % (k, n, 100.0 * n / total))
    print()
    print("combinations:")
    for combo, n in sorted(combos.items(), key=lambda kv: -kv[1]):
        print("  %-34s %4d  (%.1f%%)" % ("+".join(sorted(combo)) or "(none)", n, 100.0 * n / total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
