"""Cross-check: do the `type-absent` members fall inside the already-closed 17 triage types? (R708d)

If they do, that bucket introduces no new gap -- it is the same population criterion (a) already adjudicated, counted
per member instead of per type. If they do not, there is a type nobody has triaged yet and that must be said.

Written as a file because the inline version lost a backtick to shell quoting.
"""

import io
import json
import re
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import c10_split as S


def main():
    bindings = json.load(io.open(S.BINDINGS, encoding="utf-8"))
    renames = S.renames()
    classes = S.source_classes()

    absent, per_type = set(), {}
    for full_type, members in bindings.items():
        simple, resolved = S.resolve(full_type, renames)
        if not (classes.get(resolved) or classes.get(simple) or classes.get(simple.split(chr(96))[0])):
            absent.add(simple)
            per_type[simple] = per_type.get(simple, 0) + len(members)

    total = sum(per_type.values())
    print("type-absent: %d members across %d types" % (total, len(per_type)))
    for t, n in sorted(per_type.items(), key=lambda kv: -kv[1]):
        print("  %-46s %3d" % (t, n))

    triage = io.open(r"D:\projects\cyber-reverse\docs\TYPE_PRESENCE_TRIAGE.md", encoding="utf-8").read()
    known = set()
    for line in triage.splitlines():
        m = re.match(r"\| `([^`]+)` \|", line)
        if m:
            known.add(m.group(1).strip())
            # `ObservableDictionary`2` -> also record the bare name before the arity marker
            known.add(m.group(1).split("`")[0].strip())

    print()
    print("triage rows: %d types" % len([l for l in triage.splitlines() if re.match(r"\| `", l)]))
    outside = sorted(t for t in per_type if t not in known and t.split("`")[0] not in known)
    print("type-absent types NOT in the triage: %s" % (outside if outside else "none -- all already triaged"))
    return 0 if not outside else 1


if __name__ == "__main__":
    sys.exit(main())
