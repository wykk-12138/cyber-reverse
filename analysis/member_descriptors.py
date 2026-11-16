"""For each undeclared binding member, quote the original's own descriptor proving it is real. (R712)

**Why this exists** (project convention §1.2): `c10_split.py` says which members the replica's source does not declare,
but not whether the original actually binds them. R710 showed the difference matters: I judged twelve names implausible
and called them extractor artifacts, and the string pool refuted it. Checking one member at a time invites exactly that
mistake, because a plausible-sounding reason is cheaper than the command that settles it.

So the evidence is gathered for the whole bucket in one pass. `analysis/_xaml_bindings.py` reads Avalonia compiled-XAML
descriptors of the form

    <Namespace.Type>,<Owner.Namespace>.<Member>!Getter

out of `pe_strings.txt`. This walks the same file once, indexes every descriptor by (type simple name, member), and then
reports, for each undeclared member, whether the original carries a binding for it and in which direction.

**Criterion, fixed before measuring**: a member is `bound-in-original` when a descriptor names that member on that type
with Getter or Setter; `no-descriptor` otherwise. `no-descriptor` is not evidence of absence from the original -- the
binding may be spelled in a way this regex does not cover -- so those members must not be claimed either way.
"""

import io
import json
import re
import sys

STRINGS = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
BINDINGS = r"D:\projects\cyber-reverse\replica\docs\xaml_bindings.json"

DESC = re.compile(r"(Cybersole[\w.`]*?),([\w.`]+?)!(Getter|Setter)")


def index_descriptors():
    """{(type simple name, member): {kinds}} over every descriptor in the string pool."""
    out = {}
    total = 0
    with io.open(STRINGS, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            for m in DESC.finditer(line):
                typ, owner, kind = m.group(1), m.group(2), m.group(3)
                if not typ.startswith("Cybersole."):
                    continue
                total += 1
                type_simple = typ.split(".")[-1]
                member = owner.split(".")[-1]
                out.setdefault((type_simple, member), set()).add(kind)
    return out, total


def main(argv):
    sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
    import c10_split as S

    descriptors, total = index_descriptors()
    print("descriptors indexed from pe_strings.txt: %d across %d (type, member) keys"
          % (total, len(descriptors)))
    print()

    bindings = json.load(io.open(BINDINGS, encoding="utf-8"))
    renames = S.renames()
    bodies, bases = S.source_classes()
    visible = S.visible_symbols()

    rows = []
    for full_type, members in sorted(bindings.items()):
        simple, resolved = S.resolve(full_type, renames)
        have = bodies.get(resolved) or bodies.get(simple) or bodies.get(simple.split("`")[0])
        for member in members:
            if S.is_visible(visible, resolved, member):
                continue
            if not have:
                continue
            if S.declares_in_chain(bodies, bases, resolved, member) or \
               S.declares_in_chain(bodies, bases, simple.split("`")[0], member):
                continue
            keys = [k for k in ((simple, member), (simple.split("`")[0], member)) if k in descriptors]
            kinds = sorted(set().union(*[descriptors[k] for k in keys])) if keys else []
            rows.append((full_type, member, kinds))

    print("undeclared members: %d" % len(rows))
    bound = [r for r in rows if r[2]]
    unbound = [r for r in rows if not r[2]]
    print("  descriptor present: %d" % len(bound))
    print("  no descriptor found: %d" % len(unbound))
    print()

    if argv and argv[0] == "--bound":
        print("=== descriptor present (the original binds these) ===")
        for t, m, kinds in bound:
            print("  %-52s %-16s %s" % (t.split(".")[-1], m, "/".join(kinds)))
    if argv and argv[0] == "--unbound":
        print("=== no descriptor found (do NOT claim either way without another source) ===")
        for t, m, _k in unbound:
            print("  %-52s %s" % (t.split(".")[-1], m))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
