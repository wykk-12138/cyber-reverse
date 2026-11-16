"""Explain the 2-member gap between `aot_member_coverage.py` (12) and `c10_split.py` (14). (R708b)

Two tools, same question, answers two apart. One of the following must be true and it decides which number is right:

  * the coverage tool keys on the ORIGINAL type name and my split keys on the triage's RENAMED name, so a member
    that survives under the new name counts for me and not for it; or
  * the coverage tool applies some other filter I do not, and MY 14 is the inflated one.

This prints both membership lists for the types involved so the difference is a name, not an opinion.
"""

import io
import json
import os
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import c10_split as S   # reuse the parsing rather than reimplementing it


def main():
    bindings = json.load(io.open(S.BINDINGS, encoding="utf-8"))
    renames = S.renames()
    symbol_names = S.visible_symbols()

    print("renames known to the triage: %d" % len(renames))
    for k, v in sorted(renames.items()):
        print("  %-32s -> %s" % (k, v))
    print()

    mine, theirs = set(), set()
    for full_type, members in bindings.items():
        simple = full_type.split(".")[-1]
        resolved = renames.get(simple, simple)
        for member in members:
            # mine: rename-aware
            if S.is_visible(symbol_names, resolved, member):
                mine.add((simple, member))
            # theirs: original simple name only
            if S.is_visible(symbol_names, simple, member):
                theirs.add((simple, member))

    print("rename-aware  visible: %d" % len(mine))
    print("original-name visible: %d" % len(theirs))
    print()
    print("only rename-aware (these are the members the coverage tool cannot see):")
    for t, m in sorted(mine - theirs):
        print("  %-40s %s   (source type: %s)" % (t, m, renames.get(t, "-")))
    print()
    print("only original-name (would mean my side lost something):")
    for t, m in sorted(theirs - mine):
        print("  %-40s %s" % (t, m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
