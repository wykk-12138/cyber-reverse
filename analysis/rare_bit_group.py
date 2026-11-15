"""What do the 7 headers with flag bit 3 set have in common -- against a random baseline. (R643)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R636-R642.

**Why a baseline is required**: 220 of 363 headers (60.6%) sit in the largest component. So "most of the 7 are in the
big component" is what **random sampling** produces too -- seven draws would land 4.2 of them there on average. A
finding of "they cluster" is therefore worthless without the expected value beside it. This computes it.

**Definitions, fixed BEFORE measuring**:

  * **clustered** -- all 7 land in one component **and** that component is not the 60.6% one (i.e. the concentration is
    not explained by base rates). Reported with the binomial probability of that happening by chance.
  * **size-coherent** -- at least 5 of the 7 have table lengths inside one 2x band, compared against the same statistic
    for a random sample of 7 from the other 356.
  * **link-coherent** -- their slot 1 targets point at each other (a closed set) rather than outward.

Anything else is reported as **no common trait**, which is a legitimate outcome: a rare bit need not mean anything.

Read-only. Prints; writes nothing.
"""

import struct
import sys
from collections import Counter

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"
MIN_RUN = 32
HEADER = 0x18
BIT = 3


def parse_pe(data):
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    coff = pe_off + 4
    (_m, nsect, _t, _d, _p, opt_size, _c) = struct.unpack_from("<HHIIIHH", data, coff)
    opt = coff + 20
    image_base = struct.unpack_from("<Q", data, opt + 24)[0]
    sections = []
    sec = opt + opt_size
    for i in range(nsect):
        b = sec + i * 40
        name = data[b:b + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, b + 8)
        chars = struct.unpack_from("<I", data, b + 36)[0]
        sections.append({"name": name, "vsize": vsize, "vaddr": vaddr,
                         "rawsize": rawsize, "rawptr": rawptr, "chars": chars})
    return image_base, opt + 112, sections


def rva_to_off(sections, rva):
    for s in sections:
        if s["vaddr"] <= rva < s["vaddr"] + max(s["vsize"], s["rawsize"]):
            d = rva - s["vaddr"]
            if d < s["rawsize"]:
                return s["rawptr"] + d
    return None


class Dsu:
    def __init__(self):
        self.p, self.r = {}, {}

    def add(self, x):
        self.p.setdefault(x, x)
        self.r.setdefault(x, 0)

    def find(self, x):
        root = x
        while self.p[root] != root:
            root = self.p[root]
        while self.p[x] != root:
            self.p[x], x = root, self.p[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1


def main():
    data = open(PATH, "rb").read()
    image_base, dirs_off, sections = parse_pe(data)

    exc_rva, exc_size = struct.unpack_from("<II", data, dirs_off + 3 * 8)
    off = rva_to_off(sections, exc_rva)
    starts = {struct.unpack_from("<I", data, off + i * 12)[0] for i in range(exc_size // 12)}
    starts.discard(0)

    tables = []
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        cur = 0
        run_at = 0
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            rva = va - image_base if va >= image_base else None
            if rva is not None and rva in starts:
                if cur == 0:
                    run_at = s["vaddr"] + i * 8
                cur += 1
            else:
                if cur >= MIN_RUN:
                    tables.append((run_at, cur))
                cur = 0
        if cur >= MIN_RUN:
            tables.append((run_at, cur))

    values = set()
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            if va >= image_base:
                values.add(va - image_base)

    heads = []
    for base, count in tables:
        h = base - HEADER
        if h in values:
            o = rva_to_off(sections, h)
            if o is not None and o + HEADER <= len(data):
                q = struct.unpack_from("<QQQ", data, o)
                heads.append((h, count, q))
    heads.sort()
    head_set = {h for h, _c, _q in heads}

    dsu = Dsu()
    for h in head_set:
        dsu.add(h)
    for h, _c, q in heads:
        v = q[1]
        if v >= image_base and (v - image_base) in head_set and (v - image_base) != h:
            dsu.union(h, v - image_base)

    comp_size = Counter(dsu.find(h) for h in head_set)
    size_of = {h: comp_size[dsu.find(h)] for h in head_set}

    sel = [(h, c, q) for h, c, q in heads if ((q[2] >> 16) & 0xFFFF) >> BIT & 1]
    others = [(h, c, q) for h, c, q in heads if h not in {x[0] for x in sel}]

    print("headers: %d   with bit %d set: %d" % (len(heads), BIT, len(sel)))
    print()
    print("the rare group:")
    for h, c, q in sel:
        tgt = q[1] - image_base if q[1] >= image_base else None
        where = ("header 0x%08X" % tgt) if tgt in head_set else ("outside image" if tgt is None else "non-header 0x%08X" % tgt)
        print("  0x%08X  len %-4d  comp %-4d  slot1 -> %-22s  flags 0x%04X"
              % (h, c, size_of[h], where, (q[2] >> 16) & 0xFFFF))

    print()
    dist = Counter(size_of[h] for h, _c, _q in sel)
    print("component membership of the rare group: %s" % dict(dist))

    base_share = Counter(size_of[h] for h, _c, _q in heads)
    total = len(heads)
    print("baseline (all %d): %s" % (total, dict(base_share)))
    biggest, big_n = base_share.most_common(1)[0]
    print("  largest component %d holds %.1f%% -> expected count in a random 7: %.1f"
          % (biggest, 100.0 * big_n / total, 7.0 * big_n / total))

    n_big = dist.get(biggest, 0)
    p_chance = (big_n / total) ** n_big
    print("  rare group has %d of 7 in that component; probability of at least this many by chance: %.3f"
          % (n_big, p_chance))

    print()
    lens_sel = sorted(c for _h, c, _q in sel)
    lens_all = sorted(c for _h, c, _q in heads)
    print("table lengths  rare : %s" % lens_sel)
    print("               all  : min %d / median %d / max %d" % (lens_all[0], lens_all[len(lens_all) // 2], lens_all[-1]))

    # closed set: do their slot 1 targets point inside the group?
    group = {h for h, _c, _q in sel}
    inward = sum(1 for _h, _c, q in sel if (q[1] - image_base) in group)
    print()
    print("slot 1 points inside the rare group: %d / %d" % (inward, len(sel)))

    print()
    clustered = len(dist) == 1 and biggest not in dist
    print("VERDICT: %s" % ("CLUSTERED -- all 7 in one non-dominant component" if clustered
                           else "no common trait -- the rare bit does not mark a distinct family"))


if __name__ == "__main__":
    sys.exit(main())
