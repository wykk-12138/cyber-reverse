"""Connected components of the 363 headers under slot 1. (R640)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636: 1.7-2.4 GB free
against a 1.4 GB `.i64`). Same file-only route as R636-R639.

**Data vs sentinel, fixed BEFORE measuring** -- R639's classifier treated "not found" (`?`) as a section name and gave
two non-pointer slots 100% confidence. The same mistake must not recur here, so every return value is named:

  * `image_base` bound: a slot-1 value **below** `image_base` is **not a candidate edge** (counted as `below_base`).
    It is not a self-loop and it is not a vertex.
  * `outside`: a slot-1 value that is an address but **not** one of the 363 headers. It is **not an edge**
    (counted as `outside`), because the graph is defined over the header set only.
  * `edge`: a slot-1 value that hits a header. Only these enter the union-find.

**Verdict rule, also fixed before measuring** (components are computed over an undirected graph, since a hierarchy edge
may be stored either direction):

  * **HIERARCHY** -- components >= 5 and the largest holds <= 60% of vertices: a partition into families
  * **NEAR-CONNECTED** -- largest component holds >= 90%: slot 1 is not a hierarchy edge
  * **FRAGMENTED** -- components > vertices / 4: mostly isolated pairs, not a usable structure
  * anything else -- reported as-is, no label

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
        self.parent = {}
        self.rank = {}

    def add(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


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
    print("headers: %d" % len(heads))

    dsu = Dsu()
    for h in head_set:
        dsu.add(h)

    below_base = 0
    outside = 0
    edges = 0
    self_loops = 0
    for h, _c, q in heads:
        v = q[1]
        if v < image_base:
            below_base += 1
            continue
        rva = v - image_base
        if rva in head_set:
            if rva == h:
                self_loops += 1
                continue
            dsu.union(h, rva)
            edges += 1
        else:
            outside += 1

    print()
    print("slot 1 classification (every outcome named):")
    print("  below image_base (not a candidate edge) : %d" % below_base)
    print("  address but not a header (not an edge)  : %d" % outside)
    print("  self-loop (not an edge)                 : %d" % self_loops)
    print("  edges entering union-find               : %d" % edges)

    comp = Counter()
    for h in head_set:
        comp[dsu.find(h)] += 1

    sizes = sorted(comp.values(), reverse=True)
    print()
    print("connected components (undirected):")
    print("  components : %d" % len(sizes))
    print("  sizes      : %s%s" % (sizes[:20], " ..." if len(sizes) > 20 else ""))
    if sizes:
        print("  largest    : %d (%.1f%% of %d vertices)" % (sizes[0], 100.0 * sizes[0] / len(head_set), len(head_set)))
        print("  singletons : %d" % sum(1 for s in sizes if s == 1))

    n = len(head_set)
    print()
    if sizes and len(sizes) >= 5 and sizes[0] <= 0.60 * n:
        print("VERDICT: HIERARCHY -- %d components, largest %.0f%% of vertices" % (len(sizes), 100.0 * sizes[0] / n))
    elif sizes and sizes[0] >= 0.90 * n:
        print("VERDICT: NEAR-CONNECTED -- largest holds %.0f%%; slot 1 is not a hierarchy edge" % (100.0 * sizes[0] / n))
    elif sizes and len(sizes) > n / 4:
        print("VERDICT: FRAGMENTED -- %d components over %d vertices; mostly isolated pairs" % (len(sizes), n))
    else:
        print("VERDICT: unlabelled shape -- %d components, largest %d/%d" % (len(sizes), sizes[0] if sizes else 0, n))


if __name__ == "__main__":
    sys.exit(main())
