"""Quote the raw descriptor strings for the seven command-shaped Getter/Setter members. (R714)

The previous round could not decide whether `AccountGroupView.Save` and its six siblings are commands or writable
properties, because a descriptor gives a name and a direction and nothing about type. This pulls the full strings --
including the Owner part, whose namespace says where the member is declared -- and prints the surrounding bytes, since
the string pool keeps descriptors packed together and neighbours sometimes identify the type.

**Criterion, fixed before measuring**: the round succeeds if the raw strings settle the type question for at least one
member; otherwise it records exactly what was inspected and why it is not enough, and the members stay undecided.
"""

import io
import re

STRINGS = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"

TARGETS = [
    ("AccountGroupView", "Save"),
    ("CreateGroupModal", "Create"),
    ("ProxyGroupView", "Reset"),
    ("ProxyGroupView", "Save"),
    ("SmartActionsView", "Export"),
    ("TaskGroupView", "Link"),
    ("TaskView", "Edit"),
]


def main():
    text = io.open(STRINGS, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()

    for type_simple, member in TARGETS:
        print("=== %s.%s ===" % (type_simple, member))
        found = 0
        for line in lines:
            if type_simple not in line:
                continue
            for m in re.finditer(
                    r"(Cybersole[\w.`]*?\.%s),(Cybersole[\w.`]*?)!(Getter|Setter)" % re.escape(type_simple), line):
                if m.group(2).split(".")[-1] != member:
                    continue
                print("  %s" % m.group(0))
                found += 1
            if found:
                break
        if not found:
            print("  (no exact descriptor matched -- searching loosely)")
            for line in lines:
                if type_simple in line and member in line:
                    idx = line.find(member)
                    print("  ...%s..." % line[max(0, idx - 90):idx + 60].strip())
                    break
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
