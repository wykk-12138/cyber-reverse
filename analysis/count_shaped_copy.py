"""Find count-shaped copy and whether its siblings and consumers exist. (R752)

R750 found that count-shaped labels carry three sentences (0 / 1 / n) while name-shaped ones carry two, and R751 turned
that into a discriminator. The consequence for measurement is that `analysis/witness_ranking.py` only ever surfaced the
`{0}` sentence: `No Filters` and `1 Filter Saved` have no placeholder, so a placeholder-based ranking cannot see them at
all, and the blind spot is not spread evenly -- it lands exactly on the count-shaped texts.

This script takes the other direction. Instead of asking "which functions reference a placeholder text", it asks, for
every catalogue key whose sentence starts with `{0}`:

  * which 0-case and 1-case siblings exist in the catalogue, and
  * whether the replica's source consumes the key at all.

A row with a sibling the ranking never showed, or with no consumer, is a place worth reading next.

**Why not an existing tool** (AGENTS.md §1.2): this is a question about the locale catalogue and the replica's own
source, not about the binary. `witness_ranking.py` answers a different question (function -> keys -> placeholders), and
the locale file is plain JSON. The only non-trivial part is walking the C# tree, which the repo does not already do for
this purpose.
"""

import io
import json
import os
import re
import sys

ROOT = r"D:\projects\cyber-reverse\replica"
LOCALE = os.path.join(ROOT, "src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json")
SRC = os.path.join(ROOT, "src")

# a key's sentence beginning with {0} and continuing with a noun: the n-case of a count triple
COUNT_START = re.compile(r"^\{0\} ")


def load_locale():
    return json.load(io.open(LOCALE, encoding="utf-8"))


def replica_sources():
    for dirpath, dirnames, filenames in os.walk(SRC):
        dirnames[:] = [d for d in dirnames if d not in ("obj", "bin")]
        for name in filenames:
            if name.endswith(".cs"):
                yield os.path.join(dirpath, name)


def uses(needle, blobs):
    """True when a C# file references the key. Keys are used in two forms here: the full dotted key, and a shortened
    form produced by a local helper (e.g. 'StatusParseFailed' for 'ProfileCsv.Status.ParseFailed'), so match on the
    last segment too."""
    return any(needle in blob for blob in blobs)


def main():
    loc = load_locale()
    blobs = [io.open(p, encoding="utf-8", errors="replace").read() for p in replica_sources()]
    print("  catalogue keys: %d    replica source files: %d" % (len(loc), len(blobs)))
    print()

    count_keys = sorted(k for k, v in loc.items() if isinstance(v, str) and COUNT_START.match(v))
    print("  count-shaped keys (text starts with '{0} '): %d" % len(count_keys))
    print()

    rows = []
    for key in count_keys:
        # split into (prefix, leaf): sibling keys live under the same prefix
        head, _, leaf = key.rpartition(".")
        if not head:
            continue
        siblings = sorted(k for k in loc if k.startswith(head + ".") and k != key)
        # a 0-case is a sibling whose text starts with "No "; a 1-case starts with the digit 1
        zero = [k for k in siblings if str(loc[k]).startswith("No ")]
        one = [k for k in siblings if str(loc[k]).startswith("1 ")]
        last = leaf
        used = uses(key, blobs) or uses(last, blobs)
        rows.append((key, leaf, loc[key], zero, one, used))

    triples = [r for r in rows if r[3] and r[4]]
    print("  with BOTH a 0-case and a 1-case sibling (the 0/1/n shape): %d" % len(triples))
    for key, leaf, text, zero, one, used in triples:
        mark = "used" if used else "** NO CONSUMER **"
        print("    %-46s %-22s %s" % (key, mark, text[:40]))
        print("        0-case: %-34s  1-case: %s" % (zero[0].rpartition(".")[2], one[0].rpartition(".")[2]))
    print()

    partial = [r for r in rows if bool(r[3]) != bool(r[4])]
    print("  with only ONE of the two siblings: %d" % len(partial))
    for key, leaf, text, zero, one, used in partial:
        have = "0-case only" if zero else "1-case only"
        mark = "used" if used else "NO CONSUMER"
        print("    %-46s %-14s %-13s %s" % (key, have, mark, text[:34]))
    print()

    unconsumed = [r for r in rows if not r[5]]
    print("  count-shaped keys the replica never references: %d of %d" % (len(unconsumed), len(rows)))
    for key, leaf, text, zero, one, used in unconsumed:
        print("    %-50s %r" % (key, text[:44]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
