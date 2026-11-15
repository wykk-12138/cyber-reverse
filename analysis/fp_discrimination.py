"""Is the fingerprint discriminating enough to pair functions? (R572)

Two levels measured against each other, because the level-1 answer decides whether level 2 was worth running:

  L1  (size, nblocks)
  L2  (size, nblocks, ncallees, nstrrefs)

Pure file analysis — no IDA, no target. Every number below is counted from the dumped TSVs.
"""

import collections
import io
import os

BASE = r"D:\projects\cyber-reverse\analysis"


def load(path, level):
    rows = []
    with io.open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if level == 1:
                if len(parts) < 4:
                    continue
                rows.append((int(parts[1]), int(parts[2])))
            else:
                if len(parts) < 6:
                    continue
                rows.append((int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))
    return rows


def report(label, rows):
    counts = collections.Counter(rows)
    unique = sum(1 for n in counts.values() if n == 1)
    print("%s" % label)
    print("   rows                       : %d" % len(rows))
    print("   distinct fingerprints      : %d" % len(counts))
    print("   rows with a UNIQUE key     : %d  (%.2f%%)" % (unique, 100.0 * unique / max(1, len(rows))))
    print("   largest bucket             : %d functions share one key" % max(counts.values()))
    pair_pool = sum(n for n in counts.values() if n <= 4)
    print("   rows in a bucket of <= 4   : %d  (%.2f%%)" % (pair_pool, 100.0 * pair_pool / max(1, len(rows))))
    print()
    return counts


def main():
    l1 = os.path.join(BASE, "_fp_orig.tsv")
    l2 = os.path.join(BASE, "_fp_orig_L2.tsv")

    if os.path.exists(l1):
        report("L1  (size, nblocks) — the original", load(l1, 1))
    if os.path.exists(l2):
        c2 = report("L2  (size, nblocks, ncallees, nstrrefs) — the original", load(l2, 2))
        print("L2 top 8 most common fingerprints:")
        for key, n in c2.most_common(8):
            print("   size=%-5d nblocks=%-3d ncallees=%-3d nstrrefs=%-3d -> %d"
                  % (key[0], key[1], key[2], key[3], n))


if __name__ == "__main__":
    main()
