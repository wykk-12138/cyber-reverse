"""Do the 19 components align with the 18 flag values in slot 2's middle 16 bits? (R641)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R636-R640.

**Why this test**: R640 found 19 components with three families covering 91.7%, but the pre-registered rule called the
shape unlabelled (60.6% against a 60% bound). Rather than move a threshold, this asks a question that does **not**
depend on the hierarchy hypothesis at all: is there any relation between the grouping and the 18 flag values?

**Definition, fixed BEFORE measuring**: for each component, *purity* = the share of its members carrying the
component's most common flag value. A component is **pure** at >= 90%.

  * **ALIGNED**   -- at least 3 components are pure **and** they cover >= 50% of the 363 vertices
  * **UNALIGNED** -- no component reaches 60% purity
  * **PARTIAL**   -- anything else

No sentinel applies here: slot 2's middle 16 bits are always a value, never "not found".

Read-only. Prints; writes nothing.
"""

import struct
import sys
from collections import Counter

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"
MIN_RUN = 32
HEADER = 0x18


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
        self.p = {}
        self.r = {}

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
        if v >= image_base:
            rva = v - image_base
            if rva in head_set and rva != h:
                dsu.union(h, rva)

    groups = {}
    for h, count, q in heads:
        root = dsu.find(h)
        flag = (q[2] >> 16) & 0xFFFF
        groups.setdefault(root, []).append((h, count, flag))

    print("components: %d   vertices: %d" % (len(groups), len(head_set)))
    global_flags = Counter(f for g in groups.values() for _h, _c, f in g)
    print("flags overall: %d distinct" % len(global_flags))

    print()
    print("per-component purity (share of the most common flag value):")
    ordered = sorted(groups.values(), key=lambda g: -len(g))
    pure = 0
    pure_cover = 0
    for g in ordered[:10]:
        fc = Counter(f for _h, _c, f in g)
        top, n = fc.most_common(1)[0]
        purity = n / len(g)
        if purity >= 0.90 and len(g) >= 3:
            pure += 1
            pure_cover += len(g)
        print("  size %-4d purity %5.1f%%  top flag 0x%04X  flags in group: %d"
              % (len(g), purity * 100, top, len(fc)))

    # all components, not just the top 10
    for g in ordered:
        fc = Counter(f for _h, _c, f in g)
        top, n = fc.most_common(1)[0]
        purity = n / len(g)
        if purity >= 0.90 and len(g) >= 3 and g not in ordered[:10]:
            pure += 1
            pure_cover += len(g)

    print()
    print("summary:")
    print("  components pure at >=90%% (size >=3) : %d" % pure)
    print("  vertices covered by those           : %d / %d" % (pure_cover, len(head_set)))

    print()
    if pure >= 3 and pure_cover >= 0.50 * len(head_set):
        print("VERDICT: ALIGNED -- the grouping tracks the flag value")
    elif all((Counter(f for _h, _c, f in g).most_common(1)[0][1] / len(g)) < 0.60 for g in groups.values()):
        print("VERDICT: UNALIGNED -- no component reaches 60% purity; grouping is independent of the flag")
    else:
        print("VERDICT: PARTIAL -- some components concentrate, none enough to call it aligned")


if __name__ == "__main__":
    sys.exit(main())
