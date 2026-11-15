"""Cross-binary matching by canonical instruction hash (R573).

The decisive test that R572's negative result left open. Same key family on both sides:

    Cybersole.exe            (original, .NET 10 AOT)  203,878 eligible functions
    Cybersole.Ui.exe         (replica,  .NET  8 AOT)  137,267 eligible functions

Both dumps come from `analysis/dump_function_hashes.py` run inside IDA, so the hash definition is identical.

What the numbers mean, and what they do not:

* A hash that is **unique on both sides** is a 1:1 candidate. That count is the honest headline.
* A hash shared by several functions on either side yields *no* pairing — it is a bucket, not a match.
* A match by template is **structural similarity, never behavioural equality**. Two functions can share an
  instruction template and compute different things (different constants are normalised away, jump targets are
  normalised away). Every pair found here is a candidate for manual comparison, not a proof.

Also reported: how many original-side functions are *unique but unmatched* — those are the real gap, because a
unique template that has no counterpart means either the code is missing or the .NET 10 vs .NET 8 builds diverged
(inlining, devirtualisation), and this data cannot tell those two apart.
"""

import collections
import io

BASE = r"D:\projects\cyber-reverse\analysis"


def load(path):
    """hash -> list of (start_ea, size, insns, name)"""
    table = collections.defaultdict(list)
    with io.open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            table[p[3]].append((p[0], p[1], p[2], p[4]))
    return table


def main():
    orig = load(BASE + r"\_fp_orig_H.tsv")
    rep = load(BASE + r"\_fp_rep_H.tsv")

    print("=== distinct canonical hashes ===")
    print("  original : %d hashes over %d functions" % (len(orig), sum(len(v) for v in orig.values())))
    print("  replica  : %d hashes over %d functions" % (len(rep), sum(len(v) for v in rep.values())))

    both = set(orig) & set(rep)
    print()
    print("=== intersection ===")
    print("  hashes present on BOTH sides : %d" % len(both))
    print("  original-only hashes         : %d" % len(set(orig) - set(rep)))
    print("  replica-only hashes          : %d" % len(set(rep) - set(orig)))

    one_to_one = [h for h in both if len(orig[h]) == 1 and len(rep[h]) == 1]
    print()
    print("=== the only defensible pairing ===")
    print("  hashes unique on BOTH sides (1:1 candidates) : %d" % len(one_to_one))
    print("  -> that is %.2f%% of the original's eligible functions"
          % (100.0 * len(one_to_one) / max(1, sum(len(v) for v in orig.values()))))

    orig_unique = [h for h in orig if len(orig[h]) == 1]
    matched_unique = [h for h in orig_unique if h in rep]
    print()
    print("=== where the gap is ===")
    print("  original-side UNIQUE templates                : %d" % len(orig_unique))
    print("  ... of which a replica function also has it   : %d  (%.1f%%)"
          % (len(matched_unique), 100.0 * len(matched_unique) / max(1, len(orig_unique))))
    print("  ... of which nothing on the replica matches    : %d"
          % (len(orig_unique) - len(matched_unique)))

    print()
    print("=== 12 sample 1:1 candidates (original sub_* -> replica name) ===")
    shown = 0
    for h in one_to_one:
        if shown >= 12:
            break
        o = orig[h][0]
        r = rep[h][0]
        print("  %-14s size=%-5s insns=%-4s  ->  %-58s size=%-5s insns=%s"
              % (o[3], o[1], o[2], r[3][:58], r[1], r[2]))
        shown += 1


if __name__ == "__main__":
    main()
