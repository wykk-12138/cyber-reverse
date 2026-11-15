"""Repair only the C# generic-arity signature; dry run first.

The damage has one identifiable shape: a C# generic arity written ``Name\\`N`` (escaped backtick before a digit) lost its
backslash and became ``Name`N``. That is what leaves the surrounding code span unbalanced, and it is what appears on
every odd-backtick line in BLOCKERS.md.

VERDICT.md's 33 odd lines are mostly **multi-line code spans** that were odd per line before any edit (a span opened on
one line and closed on the next), so they are excluded from the repair.

Rule: insert a backslash before a backtick that is immediately followed by a digit and immediately preceded by a
letter or a dot. Everything else is untouched, and anything not matching is reported as residual Unknown.
"""

import io
import re

FILES = [
    r"D:\projects\cyber-reverse\docs\BLOCKERS.md",
    r"D:\projects\cyber-reverse\replica\docs\VERDICT.md",
]

# a backtick followed by a digit, preceded by a letter or dot -> restore the escape
PATTERN = re.compile("([A-Za-z.])(`)(?=\\d)")


def main(dry_run=True):
    for p in FILES:
        text = io.open(p, encoding="utf-8").read()
        hits = list(PATTERN.finditer(text))
        print("%-24s generic-arity candidates: %d" % (p.split("\\")[-1], len(hits)))
        for m in hits[:10]:
            lo = max(0, m.start() - 28)
            print("   %r" % text[lo:m.end() + 4])
        if hits and not dry_run:
            repaired = PATTERN.sub(lambda m: m.group(1) + "\\" + "`", text)
            io.open(p, "w", encoding="utf-8").write(repaired)
            print("   -> repaired")
    if dry_run:
        print()
        print("DRY RUN -- nothing written. Re-run with dry_run=False to apply.")


if __name__ == "__main__":
    main(dry_run=True)
