"""List the seven matched pairs that involve Cybersole's own code (R574).

R573's cross-binary hash match produced 2,404 one-to-one candidates, of which only 7 carry a `Cybersole_*` name on
the replica side. Those seven are the only structural evidence that points at the application layer rather than at
the shared runtime substrate, so they are worth naming before any further work.

Pure file analysis — no IDA, no target.
"""

import collections
import io

BASE = r"D:\projects\cyber-reverse\analysis"


def load(path):
    table = collections.defaultdict(list)
    with io.open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                table[p[3]].append((p[0], p[1], p[2], p[4]))
    return table


def main():
    orig = load(BASE + r"\_fp_orig_H.tsv")
    rep = load(BASE + r"\_fp_rep_H.tsv")

    pairs = [h for h in set(orig) & set(rep) if len(orig[h]) == 1 and len(rep[h]) == 1]
    mine = [(h, orig[h][0], rep[h][0]) for h in pairs if rep[h][0][3].startswith("Cybersole")]

    print("one-to-one pairs in total : %d" % len(pairs))
    print("with a Cybersole_* name   : %d" % len(mine))
    print()
    print("%-14s %-6s %-6s  %-16s %-6s %-6s  %s"
          % ("orig addr", "size", "insns", "hash", "size", "insns", "replica name"))
    for h, o, r in sorted(mine, key=lambda x: x[2][3]):
        print("%-14s %-6s %-6s  %-16s %-6s %-6s  %s"
              % (o[0], o[1], o[2], h[:16], r[1], r[2], r[3]))

    print()
    print("full replica names:")
    for h, o, r in sorted(mine, key=lambda x: x[2][3]):
        print("  orig 0x%s  ->  %s" % (o[0], r[3]))


if __name__ == "__main__":
    main()
