"""Audit the claim table against criterion (d) (R513).

Criterion (d), as the table's own header states it:

    判据 d 满足 = 每条都有 authority，且非 unknown 者都有命令。

The claims live in markdown **tables**, six columns wide:

    | id | claim | status | authority | command | gap_reason |

So the audit parses rows, not headings: for each `| Cxx | … |` row it reads the authority and command cells and
checks the two conditions. An `unknown` authority is allowed, but then status must also be unknown — otherwise the
verdict is decided without the evidence that supports it.

First run of this audit used headings and reported 17/22 "no authority"; that was the audit being wrong, not the
table. The shape is a table, so the parser reads a table.
"""

import io
import re
import sys

PATH = r"D:\projects\cyber-reverse\docs\PARITY_CLAIMS.md"

ROW = re.compile(r"^\|\s*(C-monitor-[\w-]+|C\d+[a-z]?)\s*\|(.+)\|\s*$", re.M)
AUTHORITIES = {"tool-evidence", "manual-from-command", "unknown"}


def cells(rest):
    return [c.strip() for c in rest.split("|")]


def main():
    text = io.open(PATH, encoding="utf-8").read()

    rows = []
    for m in ROW.finditer(text):
        cid = m.group(1)
        parts = cells(m.group(2))
        # parts = [claim, status, authority, command, gap_reason] (+ possible trailing empties)
        if len(parts) < 5:
            rows.append((cid, None, None, None, None))
            continue
        rows.append((cid, parts[0], parts[1], parts[2], parts[3]))

    problems = []
    unknown_count = 0
    for cid, claim, status, authority, command in rows:
        if authority is None:
            problems.append((cid, "row is shorter than the six-column shape"))
            continue
        auth = authority.strip("*` ")
        stat = (status or "").strip("*` ").lower()

        if auth not in AUTHORITIES:
            problems.append((cid, "authority is %r, not one of %s" % (auth, sorted(AUTHORITIES))))
            continue
        if auth == "unknown":
            unknown_count += 1
            if "unknown" not in stat:
                problems.append((cid, "authority unknown but status is %r" % stat))
            continue
        if not command or command in ("—", "-", ""):
            problems.append((cid, "decided verdict (%s) with no command" % stat))

    print("claims parsed: %d   (authority=unknown: %d)" % (len(rows), unknown_count))
    for cid, why in problems:
        print("  FAIL  %-22s %s" % (cid, why))
    if problems:
        print("\n%d claim(s) do not satisfy criterion (d)" % len(problems))
        sys.exit(1)
    print("criterion (d) holds: every claim has a valid authority, and every decided one has a command")


if __name__ == "__main__":
    main()
