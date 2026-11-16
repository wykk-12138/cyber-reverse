"""Are the numeric-suffixed binding members extractor dedupe markers or real names? (R709)

`EditValue`1` carries `HasMultiple_87` .. `HasMultiple_101` and `Value_92`, `Value_100`. Either the original's code really
has members named that way, or the extractor appended an index to keep repeated occurrences distinct -- and if it is the
latter, the 819 denominator is inflated and C10 reads lower than it should.

Criterion: if a bare `HasMultiple` / `Value` also appears in the same table, the suffix is a disambiguation marker.
"""

import io
import json
import re

BINDINGS = r"D:\projects\cyber-reverse\replica\docs\xaml_bindings.json"


def main():
    d = json.load(io.open(BINDINGS, encoding="utf-8"))
    keys = [k for k in d if k.endswith("EditValue`1")]
    print("keys ending with EditValue`1:", keys)
    for key in keys:
        members = d[key]
        print("  %s -> %d members" % (key, len(members)))
        print("  all: %s" % members)
        bare = sorted({m for m in members if not re.search(r"_\d+$", m)})
        suffixed = [m for m in members if re.search(r"_\d+$", m)]
        print("  bare names       : %s" % bare)
        print("  suffixed count   : %d" % len(suffixed))
        for b in bare:
            same = [m for m in suffixed if re.sub(r"_\d+$", "", m) == b]
            if same:
                print("    %-16s also appears as %s" % (b, same[:6]))

    total = sum(1 for ms in d.values() for m in ms if re.search(r"_\d+$", m))
    print()
    print("members with a numeric suffix across the whole table: %d of %d"
          % (total, sum(len(v) for v in d.values())))
    per_type = {}
    for t, ms in d.items():
        n = sum(1 for m in ms if re.search(r"_\d+$", m))
        if n:
            per_type[t.split(".")[-1]] = n
    for t, n in sorted(per_type.items(), key=lambda kv: -kv[1])[:10]:
        print("  %-46s %d" % (t, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
