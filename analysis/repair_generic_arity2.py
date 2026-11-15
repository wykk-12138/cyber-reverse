"""Repair the generic-arity signature OUTSIDE fenced code blocks; dry run first.

The previous dry run showed why the fence exclusion matters: several candidates
(`````Cybersole.Models.EditValue`1`````, ``split('`')[0]``, an IDA listing line) sit inside fenced blocks, where a bare
backtick is literal content and adding a backslash would corrupt it.

So: walk the file line by line, track fence state, and apply the generic-arity rule only to non-fenced text. Then report
the odd-backtick line count before and after, and leave anything still odd as a residual Unknown rather than touching it.
"""

import io
import re

FILES = [
    r"D:\projects\cyber-reverse\docs\BLOCKERS.md",
    r"D:\projects\cyber-reverse\replica\docs\VERDICT.md",
]

PATTERN = re.compile("([A-Za-z.])(`)(?=\\d)")
FENCE = "```"


def odd_count(lines):
    n = 0
    in_fence = False
    for line in lines:
        if line.strip().startswith(FENCE):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.count("`") % 2 == 1:
            n += 1
    return n


def transform(text):
    out = []
    in_fence = False
    changed = 0
    for line in text.splitlines(keepends=True):
        if line.strip().startswith(FENCE):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        new, n = PATTERN.subn(lambda m: m.group(1) + "\\" + "`", line)
        changed += n
        out.append(new)
    return "".join(out), changed


def main(dry_run=True):
    for p in FILES:
        text = io.open(p, encoding="utf-8").read()
        before = odd_count(text.splitlines())
        new, changed = transform(text)
        after = odd_count(new.splitlines())
        print("%-24s odd %d -> %d   subn=%d" % (p.split("\\")[-1], before, after, changed))
        if not dry_run and changed:
            io.open(p, "w", encoding="utf-8").write(new)
            print("   -> written")
    print()
    print("DRY RUN -- nothing written" if dry_run else "APPLIED")


if __name__ == "__main__":
    main(dry_run=True)
