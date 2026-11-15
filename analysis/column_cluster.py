"""Are the CSV column names a contiguous table in the pool? And does `securityCode` sit in it? (R652)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R636-R651.

**Why**: R651 found `cardCvv` absent from the pool while `securityCode` is present, and 13 of the replica's 15 column
names appear verbatim. That was Inference (medium-high). If the column names sit **together** in the pool -- the way a
column list would be compiled -- the reading becomes Observation.

**Definition, fixed before measuring**:

  * **column-name shape** -- a pooled string matching `^[a-z][a-zA-Z0-9]{2,19}$` (lowercase camel, 3-20 chars). This is
    deliberately loose: it will match many non-column strings, which is the point -- the test is whether the *known*
    column names cluster, not whether the filter is selective.
  * **clustered** -- at least 10 of the replica's 15 column names have pooled addresses inside one **4 KB window**.
  * if clustered, list **every** column-shape string inside that window: any extra one is a candidate column the
    replica is missing (the R651 failure mode).

Read-only. Prints; writes nothing.
"""

import io
import re
import sys

POOL = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
KNOWN = ["name", "email", "firstName", "lastName", "phone", "address1", "address2",
         "city", "state", "zip", "country", "cardNumber", "cardExpiry", "securityCode", "cardCvv", "cardName"]
SHAPE = re.compile(r"^[a-z][a-zA-Z0-9]{2,19}$")
WINDOW = 0x1000


def main():
    rows = []
    for line in io.open(POOL, encoding="utf-8", errors="replace").read().splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2:
            continue
        try:
            addr = int(parts[0], 16)
        except ValueError:
            continue
        rows.append((addr, parts[1].strip()))

    print("pool strings: %d" % len(rows))

    by_value = {}
    for addr, s in rows:
        by_value.setdefault(s, []).append(addr)

    present = [(k, by_value[k][0]) for k in KNOWN if k in by_value]
    absent = [k for k in KNOWN if k not in by_value]
    print()
    print("replica column names found in pool : %d / %d" % (len(present), len(KNOWN)))
    print("  absent: %s" % absent)
    print()
    print("  addresses:")
    for k, a in sorted(present, key=lambda x: x[1]):
        print("    0x%08X  %s" % (a, k))

    if not present:
        print()
        print("VERDICT: no column names pooled; nothing to cluster")
        return

    addrs = sorted(a for _k, a in present)
    best = None
    for start in addrs:
        inside = [a for a in addrs if start <= a < start + WINDOW]
        if best is None or len(inside) > len(best[1]):
            best = (start, inside)
    start, inside = best
    print()
    print("densest %d-byte window: 0x%08X .. 0x%08X holds %d of %d known names"
          % (WINDOW, start, start + WINDOW, len(inside), len(present)))

    # every column-shape string inside that window
    inside_set = set(inside)
    others = [(a, s) for a, s in rows if start <= a < start + WINDOW and SHAPE.match(s) and a not in inside_set]
    print()
    print("column-shape strings in that window that are NOT among the known ones: %d" % len(others))
    for a, s in others[:40]:
        print("    0x%08X  %s" % (a, s))

    clustered = len(inside) >= 10
    print()
    if clustered:
        print("VERDICT: CLUSTERED -- %d of %d known names within %d bytes: the pool holds a column list"
              % (len(inside), len(present), WINDOW))
        print("         any name above is a candidate column the replica does not read")
    else:
        print("VERDICT: NOT CLUSTERED -- column names are scattered; no compiled column list visible")


if __name__ == "__main__":
    sys.exit(main())
