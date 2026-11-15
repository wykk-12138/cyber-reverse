"""The `.pdata` unwind-info pointers as a second grouping clue -- ceiling first. (R645)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R636-R644.

**The subtraction first, before any probing**: R644's lesson was that a route was pursued for several rounds without
asking how many nodes it could possibly reach. So this states the ceiling before measuring anything:

  * `.pdata` holds one `RUNTIME_FUNCTION` per non-leaf function: **277,094** entries (R636).
  * IDA's `af` function count (PDB-free, equal footing) is **321,244**.
  * Ceiling of this route = **277,094 functions = 86.2% of 321,244.**

So unlike the pointer tables (1,620 functions, 0.58%), this clue can in principle cover most of the image. That is the
only reason it is worth a round.

**What is measured**: whether `UnwindInfoAddress` clusters, which would indicate compile-unit grouping.

  * **clustered** -- >= 80% of distinct unwind-info RVAs fall inside one contiguous span no larger than 25% of the
    unwind-info range. (Fixed before looking.)
  * **interleaved** -- the unwind-info RVAs of address-adjacent functions jump around the range instead.

Read-only. Prints; writes nothing.
"""

import struct
import sys
from collections import Counter

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"
CHUNK_MAX_SHARE = 0.25
CLUSTER_SHARE = 0.80


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


def main():
    data = open(PATH, "rb").read()
    image_base, dirs_off, sections = parse_pe(data)

    print("ceiling of this route (stated before probing):")
    print("  .pdata entries                 : 277,094")
    print("  IDA af functions (equal footing): 321,244")
    print("  ceiling                        : 86.2%% of the image's functions")
    print()

    exc_rva, exc_size = struct.unpack_from("<II", data, dirs_off + 3 * 8)
    off = rva_to_off(sections, exc_rva)
    n = exc_size // 12
    funcs = []
    for i in range(n):
        begin, end, unwind = struct.unpack_from("<III", data, off + i * 12)
        if begin:
            funcs.append((begin, end, unwind))
    funcs.sort()
    print("RUNTIME_FUNCTION parsed: %d" % len(funcs))

    unwinds = [u for _b, _e, u in funcs]
    distinct = set(unwinds)
    zero = sum(1 for u in unwinds if u == 0)
    print("  unwind values  : %d total, %d distinct, %d zero" % (len(unwinds), len(distinct), zero))
    if distinct:
        lo, hi = min(distinct), max(distinct)
        print("  unwind range   : 0x%08X .. 0x%08X  (span %d)" % (lo, hi, hi - lo))

    # which section holds the unwind info
    holder = Counter()
    for u in list(distinct)[:5000]:
        o = rva_to_off(sections, u)
        if o is None:
            holder["unmapped"] += 1
            continue
        for s in sections:
            if s["rawptr"] <= o < s["rawptr"] + s["rawsize"]:
                holder[s["name"]] += 1
                break
    print("  section (first 5000): %s" % dict(holder))

    # locality: bucket the distinct unwind RVAs
    BUCKETS = 64
    if distinct:
        span = hi - lo + 1
        bucket = Counter((u - lo) * BUCKETS // span for u in distinct)
        top = bucket.most_common(4)
        covered = sum(c for _k, c in top)
        print()
        print("unwind-RVA locality over %d buckets:" % BUCKETS)
        print("  top 4 buckets: %s" % top)
        print("  covered by top 4: %d / %d = %.1f%%" % (covered, len(distinct), 100.0 * covered / len(distinct)))

    # do address-adjacent functions have nearby unwind info?
    jumps = []
    for i in range(len(funcs) - 1):
        du = abs(funcs[i + 1][2] - funcs[i][2])
        jumps.append(du)
    jumps.sort()
    print()
    print("|unwind(next) - unwind(current)| across address-ordered functions:")
    print("  min %d  median %d  p90 %d  max %d" % (jumps[0], jumps[len(jumps) // 2],
                                                  jumps[int(len(jumps) * 0.9)], jumps[-1]))
    small = sum(1 for d in jumps if d <= 16)
    print("  <=16 bytes apart: %d / %d = %.1f%%" % (small, len(jumps), 100.0 * small / len(jumps)))

    print()
    if distinct and covered >= CLUSTER_SHARE * len(distinct):
        print("VERDICT: CLUSTERED -- unwind info packs into a few buckets; compile units may be separable")
    else:
        print("VERDICT: INTERLEAVED -- unwind info does not pack by address; grouping is not visible this way")


if __name__ == "__main__":
    sys.exit(main())
