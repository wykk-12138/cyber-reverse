"""Is there a country->states table in the pool? (R670)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R668/R669.

**Why**: R669 established by Observation (the Chinese sentence `{1} 中未知的州/省"{0}"`) that the original decides
"state {0} is unknown in country {1}" -- so a country->states mapping exists **somewhere**. R668 saw 15 of 28 US state
names scattered between `0x06B4BC7C` and `0x06E06E64` (a 4.5 MB span), which looks like geo data rather than a table.

**Criterion fixed before measuring**:

  * take the 50 US state names as the probe set (they are ASCII, so both dumps carry them equally);
  * slide a **4 KB window** over their pooled addresses;
  * **TABLE** -- at least **8** of the 50 land in one window (a compiled list would be contiguous);
  * **SCATTERED** -- the densest window holds fewer than 8, i.e. these names are not stored as one list.

The threshold is 8 because a real 50-state list inside 4 KB would obviously exceed it; anything below 8 means the
names are incidental occurrences, not a block. **The threshold is not moved after seeing the result.**

Also reports the same measure for the UTF-8 dump, since R669 showed the ASCII dump loses non-ASCII text; state names
are ASCII so both should agree -- if they do not, that is itself worth knowing.
"""

import io
import re
import sys

DUMPS = [
    r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
    r"D:\projects\cyber-reverse\analysis\pe_strings_utf8.txt",
]

STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma",
    "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
    "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
]

WINDOW = 0x1000
THRESHOLD = 8


def load(path):
    out = []
    for line in io.open(path, encoding="utf-8", errors="replace").read().splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2:
            continue
        try:
            out.append((int(parts[0], 16), parts[1].strip()))
        except ValueError:
            continue
    return out


def main():
    for dump in DUMPS:
        rows = load(dump)
        exact = {}
        for addr, s in rows:
            exact.setdefault(s, addr)
        found = [(s, exact[s]) for s in STATES if s in exact]
        name = dump.rsplit("\\", 1)[-1]
        print("=== %s (%d strings) ===" % (name, len(rows)))
        print("  US state names present: %d of %d" % (len(found), len(STATES)))
        if not found:
            print()
            continue
        addrs = sorted(a for _s, a in found)
        print("  address span: 0x%08X .. 0x%08X (%.1f MB)" % (addrs[0], addrs[-1], (addrs[-1] - addrs[0]) / 1048576.0))
        best = (0, 0, [])
        for start in addrs:
            inside = [a for a in addrs if start <= a < start + WINDOW]
            if len(inside) > best[0]:
                best = (len(inside), start, inside)
        count, start, inside = best
        print("  densest %d-byte window: 0x%08X holds %d" % (WINDOW, start, count))
        verdict = "TABLE" if count >= THRESHOLD else "SCATTERED"
        print("  verdict: %s (threshold %d)" % (verdict, THRESHOLD))
        if count:
            names = sorted((a, s) for s, a in found if a in inside)
            print("  names in that window: %s" % ", ".join(n for _a, n in names[:12]))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
