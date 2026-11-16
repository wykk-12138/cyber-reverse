"""Descriptor direction distribution across the whole binding table. (R714b)

Cheap, and it settles a question the round raised: how unusual is `Getter`+`Setter` on a command-named member? If most
of the 819 are G/S, the direction carries little information; if Getter-only dominates and the command-shaped names are
the G/S minority, that is itself worth recording.
"""

import io
import json
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import member_descriptors as D
import c10_split as S


def main():
    descriptors, total = D.index_descriptors()
    bindings = json.load(io.open(S.BINDINGS, encoding="utf-8"))

    both = getter = setter = neither = 0
    gs_names = []
    for full_type, members in bindings.items():
        simple, _resolved = S.resolve(full_type, S.renames())
        for member in members:
            keys = [k for k in ((simple, member), (simple.split("`")[0], member)) if k in descriptors]
            kinds = set().union(*[descriptors[k] for k in keys]) if keys else set()
            if kinds == {"Getter", "Setter"}:
                both += 1
                gs_names.append((simple, member))
            elif kinds == {"Getter"}:
                getter += 1
            elif kinds == {"Setter"}:
                setter += 1
            elif not kinds:
                neither += 1

    print("binding members           : %d" % sum(len(v) for v in bindings.values()))
    print("  Getter only            : %d" % getter)
    print("  Setter only            : %d" % setter)
    print("  Getter + Setter        : %d" % both)
    print("  no descriptor          : %d" % neither)
    print()
    print("the 18 command-shaped or writable members this round reasoned about:")
    for t, m in gs_names:
        if m in ("Save", "Create", "Reset", "Export", "Link", "Edit", "Running", "Inputs", "Name"):
            print("  %-30s %s" % (t, m))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
