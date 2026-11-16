"""Per-member accessor evidence: does the original carry get_/set_/backing-field names? (R715)

**Why this exists** (project convention §1.2): R714 measured that the descriptor direction field is nearly useless --
78% of all binding members are Getter+Setter, so it cannot separate a command from a data property. What R714 also
turned up, while probing `EditValue`1`, is a stronger and independent source: the original's string pool carries the
CLR accessor names themselves.

    get_HasMultiple     set_HasMultiple     <HasMultiple>k__BackingField

A `set_X` string means the type declares a setter for X. An `ICommand` property is normally getter-only, so the
presence or absence of `set_X` says something the descriptor direction did not.

**Criterion, fixed before measuring**: for each undeclared binding member, classify by which of the three name forms the
original carries:

    get+set+field   an auto-property with a setter            -> implement as a writable property
    get+field       an auto-property without a setter         -> read-only property or ICommand; still ambiguous
    get only        a manual getter, or an interface member   -> needs another source
    none            nothing to go on                          -> Unknown

This is name-level evidence from the original, not a guess from plausibility: it is the same class of string R710 used
to refute my "fake member" claim.
"""

import io
import json
import sys

STRINGS = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import c10_split as S
import member_descriptors as D


def collect_names():
    """{(kind, member)} present anywhere in the pool, plus the raw strings."""
    getter, setter, field = set(), set(), set()
    with io.open(STRINGS, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "get_" not in line and "set_" not in line and "BackingField" not in line:
                continue
            i = 0
            while True:
                j = line.find("get_", i)
                if j < 0:
                    break
                k = j + 4
                name = ""
                while k < len(line) and (line[k].isalnum() or line[k] == "_"):
                    name += line[k]
                    k += 1
                if name:
                    getter.add(name)
                i = j + 4
            i = 0
            while True:
                j = line.find("set_", i)
                if j < 0:
                    break
                k = j + 4
                name = ""
                while k < len(line) and (line[k].isalnum() or line[k] == "_"):
                    name += line[k]
                    k += 1
                if name:
                    setter.add(name)
                i = j + 4
            for part in line.split("<"):
                close = part.find(">k__BackingField")
                if close > 0:
                    name = part[:close].strip()
                    if name and all(c.isalnum() or c == "_" for c in name):
                        field.add(name)
    return getter, setter, field


def main(argv):
    getter, setter, field = collect_names()
    print("accessor names in the pool: get_=%d  set_=%d  backingField=%d"
          % (len(getter), len(setter), len(field)))
    print()

    descriptors, _n = D.index_descriptors()
    bindings = json.load(io.open(S.BINDINGS, encoding="utf-8"))
    renames = S.renames()
    bodies, bases = S.source_classes()
    visible = S.visible_symbols()

    rows = []
    for full_type, members in sorted(bindings.items()):
        simple, resolved = S.resolve(full_type, renames)
        have = bodies.get(resolved) or bodies.get(simple) or bodies.get(simple.split("`")[0])
        for member in members:
            if S.is_visible(visible, resolved, member) or not have:
                continue
            if S.declares_in_chain(bodies, bases, resolved, member) or \
               S.declares_in_chain(bodies, bases, simple.split("`")[0], member):
                continue
            g = member in getter
            st = member in setter
            f = member in field
            if g and st and f:
                bucket = "get+set+field"
            elif g and st:
                bucket = "get+set"
            elif g and f:
                bucket = "get+field"
            elif g:
                bucket = "get only"
            else:
                bucket = "none"
            rows.append((full_type.split(".")[-1], member, bucket))

    # (R715) THE GUARD THIS TOOL NEEDS. get_<Member> in the string pool carries no type, and a member name
    # can appear on many binding types -- Name on 37, Close on 29, Save on 17. Classifying by bare name
    # is the same error as the first version of c10_split (378/819). A name that occurs on exactly one
    # binding type CAN be attributed; anything else cannot, whatever the accessor evidence says.
    name_types = {}
    for full_type, members in bindings.items():
        simple = full_type.split(".")[-1]
        for member in members:
            name_types.setdefault(member, set()).add(simple)
    rows = [(t, m, b if len(name_types[m]) == 1 else "unattributable") for t, m, b in rows]

    counts = {}
    for _t, _m, b in rows:
        counts[b] = counts.get(b, 0) + 1
    print("undeclared members: %d" % len(rows))
    for b in ("get+set+field", "get+set", "get+field", "get only", "none", "unattributable"):
        print("  %-14s %d" % (b, counts.get(b, 0)))
    print()

    if argv and argv[0] == "--detail":
        for t, m, b in rows:
            print("  %-22s %-16s %s" % (t, m, b))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
