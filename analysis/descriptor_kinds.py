"""Descriptor kinds per member on one type. (R716)

The question this answers: `AccountGroupView.Save` carries the descriptor `...!Getter` (and a `!Setter`), while
`CheckoutView.Close` carries `!Getter` alone. If `Save` also has a `!Property` descriptor it is an AvaloniaProperty --
a writable property on the control -- which is a different thing from a CLR property used in a binding, and different
again from an ICommand. That distinction decides whether wiring the button to a command replicates the original.

**Criterion, fixed before measuring**: for each member of the given type, report the set of descriptor kinds present.
`Getter/Setter` without `Property` = a CLR property. With `Property` = an AvaloniaProperty registration.
"""

import io
import re
import sys

STRINGS = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
KINDS = ("Getter", "Setter", "Property")


def kinds_for(type_simple):
    pat = re.compile(r"(Cybersole[\w.`]*?%s),(Cybersole[\w.`]*?)!(%s)" % (re.escape(type_simple), "|".join(KINDS)))
    found = {}
    with io.open(STRINGS, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if type_simple not in line:
                continue
            for m in pat.finditer(line):
                found.setdefault(m.group(2).split(".")[-1], set()).add(m.group(3))
    return found


def main(argv):
    types = argv or ["AccountGroupView", "CheckoutView", "ProxyGroupView", "TaskGroupView"]
    for t in types:
        found = kinds_for(t)
        print("=== %s : %d members ===" % (t, len(found)))
        for mem, kinds in sorted(found.items()):
            mark = ""
            if "Property" in kinds:
                mark = "  <- AvaloniaProperty"
            elif kinds == {"Getter"}:
                mark = "  <- read-only CLR property (or ICommand)"
            elif kinds == {"Getter", "Setter"}:
                mark = "  <- writable CLR property (or ICommand with a setter)"
            print("  %-22s %-18s%s" % (mem, "/".join(sorted(kinds)), mark))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
