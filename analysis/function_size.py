"""Can function size split the 277,094 `.pdata` functions into two populations? Ceiling first. (R649)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R636-R648.

**Ceiling first** (R644/R645's lesson -- state what a route can possibly deliver before working on it):

  * `.pdata` covers **277,094** functions against IDA's 321,244 on equal footing -> **86.2%** of the image.
  * If size separates two populations, the *smaller* population's share is the ceiling for "what size can carve out".

**Method, fixed before measuring**: `size = EndAddress - BeginAddress` from each `RUNTIME_FUNCTION`. The distribution is
described by deciles, then tested for bimodality by the simplest rule that can fail:

  * **BIMODAL** -- there is a split point p such that both sides hold **>= 20%** of functions and the median of each
    side differs by **>= 4x**. That is the shape a "generated vs hand-written" boundary would have.
  * **UNIMODAL** -- no such split point: one side always falls under 20%.

Also reported: the share at <=16/<=32/<=64/<=128 bytes, since earlier rounds sampled the <=32 band as compiler glue.

Read-only. Prints; writes nothing.
"""

import struct
import sys

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"


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
    print("  .pdata functions : 277,094")
    print("  IDA af (footing) : 321,244")
    print("  ceiling          : 86.2% of the image")
    print()

    exc_rva, exc_size = struct.unpack_from("<II", data, dirs_off + 3 * 8)
    off = rva_to_off(sections, exc_rva)
    n = exc_size // 12

    sizes = []
    bad = 0
    for i in range(n):
        begin, end, _unwind = struct.unpack_from("<III", data, off + i * 12)
        if begin == 0:
            continue
        if end <= begin:
            bad += 1
            continue
        sizes.append(end - begin)

    sizes.sort()
    total = len(sizes)
    print("functions with a usable size : %d   (end <= begin: %d)" % (total, bad))
    print("min %d   max %d" % (sizes[0], sizes[-1]))
    print()
    print("deciles (bytes):")
    for q in range(1, 10):
        print("  p%-2d %6d" % (q * 10, sizes[total * q // 10]))

    print()
    print("share at or below a threshold:")
    for t in (16, 32, 64, 128, 256, 512):
        c = 0
        for s in sizes:
            if s > t:
                break
            c += 1
        print("  <= %-4d %7d  %5.1f%%" % (t, c, 100.0 * c / total))

    # bimodality: find any split with both sides >= 20% and medians >= 4x apart
    best = None
    for q in range(20, 81):
        p = sizes[total * q // 100]
        lo = [s for s in sizes if s < p]
        hi = [s for s in sizes if s >= p]
        if len(lo) < 0.20 * total or len(hi) < 0.20 * total:
            continue
        ml = lo[len(lo) // 2]
        mh = hi[len(hi) // 2]
        if ml == 0:
            continue
        ratio = mh / ml
        if ratio >= 4.0 and (best is None or ratio > best[2]):
            best = (p, (len(lo) / total, len(hi) / total), ratio, ml, mh)

    print()
    if best:
        p, shares, ratio, ml, mh = best
        print("strongest split: p=%d  low %.0f%% / high %.0f%%  medians %d vs %d (%.1fx)"
              % (p, shares[0] * 100, shares[1] * 100, ml, mh, ratio))
        print("VERDICT: BIMODAL at p=%d -- two populations are separable, smaller side is %.0f%%" %
              (p, min(shares) * 100))
    else:
        print("VERDICT: UNIMODAL -- no split gives both sides >=20% with medians >=4x apart")
        print("         so size does not carve out a 'generated vs hand-written' boundary")


if __name__ == "__main__":
    sys.exit(main())
