"""Check criterion (d) mechanically: every claim has authority, and every non-unknown claim has a command. (R811)

docs/PARITY_CLAIMS.md states the rule itself -- "判据 d 满足 = 每条都有 authority，且非 unknown 者都有命令". This applies
that rule to the table rather than reading it, so the answer is a number and not an impression.

**R978 fixed a defect that had been there since R811.** The document is not one table: it is five, one per section
(§1 structural-artifact, §2 structural-function, §3 members, §3.5 MonitorView's five commands, §4 behavioural), each
opening with its own `| id | claim | status | authority | command | gap_reason |` header. This script found the FIRST
header and stopped at the first non-table line, which is the blank before §2's heading. So it audited C1..C5 -- five of
seventeen rows -- and printed PASS. A check that covers 29% of its subject while reporting success is worse than no check,
because the number it produces gets quoted.

The fix is to walk every table in the document rather than the first one. What the verdict means is unchanged.

Reproduce:
    cd D:\\projects\\cyber-reverse
    python analysis/check_claims.py
"""

import io
import re

PATH = r"D:\projects\cyber-reverse\docs\PARITY_CLAIMS.md"
HEADER = re.compile(r"^\|\s*id\s*\|\s*claim\s*\|\s*status\s*\|\s*authority\s*\|\s*command\s*\|\s*gap_reason\s*\|")


def tables(lines):
    """Yield each claim table as a list of six-cell rows, one table per header found."""
    i = 0
    while i < len(lines):
        if HEADER.match(lines[i].strip()):
            i += 2                      # skip the header and the |---| separator
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if len(cells) >= 6:
                    rows.append(cells[:6])
                i += 1
            yield rows
            continue
        i += 1


def main():
    t = io.open(PATH, encoding="utf-8", errors="replace").read()
    all_rows = [r for table in tables(t.splitlines()) for r in table]

    print("  claim tables: %d" % sum(1 for _ in tables(t.splitlines())))
    print("  claim rows: %d" % len(all_rows))

    no_auth, no_cmd, statuses = [], [], {}
    for rid, claim, status, authority, command, gap in all_rows:
        statuses[status] = statuses.get(status, 0) + 1
        if authority in ("", "-", "?", "TODO", "—"):
            no_auth.append((rid, claim[:40]))
        # "unknown" is the status the rows use; the authority column says it too on most of them. Either reading of
        # "non-unknown" agrees, so check both and only complain when neither exempts the row.
        undecided = status.lower().startswith("unknown") or authority.lower() == "unknown"
        if not undecided and command in ("", "-", "?", "TODO", "—", "同上"):
            no_cmd.append((rid, claim[:40], status, authority))

    print("  status distribution:")
    for k, v in sorted(statuses.items(), key=lambda x: -x[1]):
        print("    %-22s %d" % (k, v))

    print()
    print("  rows without an authority: %d" % len(no_auth))
    for rid, claim in no_auth:
        print("    %-8s %s" % (rid, claim))

    print()
    print("  non-unknown rows without a command: %d" % len(no_cmd))
    for rid, claim, status, authority in no_cmd:
        print("    %-8s %-10s auth=%-12s %s" % (rid, status, authority, claim))

    verdict = "PASS" if not no_auth and not no_cmd else "FAIL"
    print()
    print("  criterion (d) by its own stated rule: %s" % verdict)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())