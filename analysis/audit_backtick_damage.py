"""Quantify and repair the backslash-before-backtick damage I caused.

What happened: `fix_backtick_artefacts.py` replaced EVERY backslash-immediately-before-a-backtick with a bare backtick
across three record files. Only a few of those were artefacts of my own R690 edit; the rest were legitimate escapes in
historical records -- C# generic arity such as ``ObservableDictionary\\`2``, and ``target\\`` written to stop a code span
from opening. There is no git in this tree, so history cannot restore them.

Repair rule, checkable rather than guessed: **a line whose backtick count is odd has a span left open**, which is what
removing an escape does. Those lines get the backslash back. Lines with an even count are left alone -- if I put a
backslash back on an even line I would break it instead.

This rule is not perfect: a line that lost two escapes stays even and will not be caught. It is reported as a residual
Unknown rather than papered over.
"""

import io

FILES = [
    r"D:\projects\cyber-reverse\docs\BLOCKERS.md",
    r"D:\projects\cyber-reverse\replica\docs\VERDICT.md",
    r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md",
]

# lines that legitimately contain a bare backtick inside a fenced block or as content are skipped
FENCE = "```"


def analyse(path):
    lines = io.open(path, encoding="utf-8").read().splitlines()
    odd = []
    in_fence = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith(FENCE):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.count("`") % 2 == 1:
            odd.append((i, line))
    return lines, odd


def main():
    grand = 0
    for p in FILES:
        lines, odd = analyse(p)
        print("%-24s odd-backtick lines: %d" % (p.split("\\")[-1], len(odd)))
        for i, line in odd[:8]:
            print("   %5d  %s" % (i, line[:120]))
        grand += len(odd)
    print()
    print("total odd lines: %d" % grand)
    print()
    print("NOTE: odd lines are CANDIDATES. Some may have been odd before my edit (e.g. an apostrophe-style")
    print("      lone backtick in prose). Nothing is changed by this script -- it only reports.")


if __name__ == "__main__":
    main()
