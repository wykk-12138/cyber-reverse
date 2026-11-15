"""Does the canonical instruction hash discriminate? (R573)

Third and last measurement in the series begun in R572. Same file-analysis approach: no IDA, no target.

  L1  (size, nblocks)                         17 s   ->  6.02 % unique   (rejected)
  L2  (size, nblocks, ncallees, nstrrefs)    128 s   -> 13.27 % unique   (rejected)
  H   canonical instruction-template SHA-256 152 s   ->  ?

A key is only useful for cross-binary pairing if a large fraction of rows are unique **within one binary**;
otherwise two sides can never be matched better than the buckets allow. The comparison below is against the
same 203,878 eligible functions in both cases, so the percentages are directly comparable.
"""

import collections
import io
import os

BASE = r"D:\projects\cyber-reverse\analysis"


def load_l1(path):
    out = []
    with io.open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4:
                out.append((int(p[1]), int(p[2])))
    return out


def load_l2(path):
    out = []
    with io.open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 6:
                out.append((int(p[1]), int(p[2]), int(p[3]), int(p[4])))
    return out


def load_h(path):
    out = []
    with io.open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                out.append((p[1], p[2], p[3]))     # size, insns, hash
    return out


def report(label, keys):
    counts = collections.Counter(keys)
    unique = sum(1 for n in counts.values() if n == 1)
    print("%-46s rows=%-7d distinct=%-7d unique=%-7d (%5.2f%%)  largest=%d"
          % (label, len(keys), len(counts), unique,
             100.0 * unique / max(1, len(keys)), max(counts.values())))
    return counts


def main():
    print("=== within the ORIGINAL binary, same 203,878 eligible functions ===")
    l1 = os.path.join(BASE, "_fp_orig.tsv")
    l2 = os.path.join(BASE, "_fp_orig_L2.tsv")
    h = os.path.join(BASE, "_fp_orig_H.tsv")

    if os.path.exists(l1):
        report("L1  (size, nblocks)", load_l1(l1))
    if os.path.exists(l2):
        report("L2  (+ ncallees, nstrrefs)", load_l2(l2))
    if os.path.exists(h):
        ch = report("H   (canonical instruction hash)", load_h(h))
        print()
        print("H: top 8 most-shared hashes")
        for key, n in ch.most_common(8):
            print("   size=%-6s insns=%-5s hash=%s -> %d" % (key[0], key[1], key[2][:16], n))
        print()
        shared = sum(n for k, n in ch.items() if n > 1)
        print("H: rows sharing their hash with at least one other function: %d (%.2f%%)"
              % (shared, 100.0 * shared / len(load_h(h))))


if __name__ == "__main__":
    main()
