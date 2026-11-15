"""Bit-level analysis of slot 2's middle 16 bits: is it an enum of 18 values, or a set of flag bits? (R642)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R636-R641.

**Definitions, fixed BEFORE measuring** (no fuzzy edges):

  * **constant bit** -- the bit holds the same value in **all 363** headers. Not "mostly", not ">=90%": all.
  * **variable bit** -- at least one header has 0 and at least one has 1.
  * **independent bit pair** -- among headers where bit A is 1, bit B takes **both** values somewhere, and vice versa.
    A pair that never varies together is *coupled*.

**Verdict rule, also fixed before measuring**:

  * **FLAG-BITS** -- >= 4 variable bits and the variable bits are pairwise independent: a real flags word
  * **ENUM** -- the 18 observed values are far fewer than the 2^(variable bits) space and every pair is coupled:
    an enumeration, not independent flags
  * **MIXED** -- anything in between

Read-only. Prints; writes nothing.
"""

import struct
import sys
from collections import Counter
from itertools import combinations

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

    mids = []
    for base, count in tables:
        h = base - HEADER
        if h in values:
            o = rva_to_off(sections, h)
            if o is not None and o + HEADER <= len(data):
                q = struct.unpack_from("<QQQ", data, o)
                mids.append((q[2] >> 16) & 0xFFFF)

    n = len(mids)
    print("headers: %d   distinct middle-16 values: %d" % (n, len(set(mids))))

    ones = [sum(1 for v in mids if (v >> b) & 1) for b in range(16)]
    constant = [b for b in range(16) if ones[b] in (0, n)]
    variable = [b for b in range(16) if b not in constant]

    print()
    print("bit occupancy (set-count over %d values):" % n)
    for b in range(15, -1, -1):
        mark = "CONST" if b in constant else "var  "
        print("  bit %2d : %4d / %d  %s" % (b, ones[b], n, mark))

    print()
    print("constant bits : %s" % constant)
    print("variable bits : %s" % variable)

    if not variable:
        print()
        print("VERDICT: no variable bit -- middle 16 is a single constant")
        return

    # independence of every variable-bit pair
    coupled = []
    independent = []
    for a, b in combinations(variable, 2):
        both = any(((x >> a) & 1) == 0 and ((x >> b) & 1) == 0 for x in mids)
        a0b1 = any(((x >> a) & 1) == 0 and ((x >> b) & 1) == 1 for x in mids)
        a1b0 = any(((x >> a) & 1) == 1 and ((x >> b) & 1) == 0 for x in mids)
        a1b1 = any(((x >> a) & 1) == 1 and ((x >> b) & 1) == 1 for x in mids)
        cells = sum([both, a0b1, a1b0, a1b1])
        if cells == 4:
            independent.append((a, b))
        else:
            coupled.append((a, b, cells))

    print()
    print("variable-bit pairs: %d independent, %d coupled (of %d)"
          % (len(independent), len(coupled), len(independent) + len(coupled)))
    if independent:
        print("  independent pairs: %s" % independent[:12])
    if coupled:
        print("  coupled examples : %s" % coupled[:8])

    space = 1 << len(variable)
    print()
    print("observed values: %d   full space over %d variable bits: %d   share: %.1f%%"
          % (len(set(mids)), len(variable), space, 100.0 * len(set(mids)) / space))

    print()
    if len(variable) >= 4 and len(independent) >= len(variable) - 1:
        print("VERDICT: FLAG-BITS -- %d variable bits, %d independent pairs" % (len(variable), len(independent)))
    elif len(set(mids)) < space / 1.5 and not independent:
        print("VERDICT: ENUM -- %d values of a %d-point space and every pair coupled" % (len(set(mids)), space))
    else:
        print("VERDICT: MIXED -- %d variable bits, %d values, %d independent pairs"
              % (len(variable), len(set(mids)), len(independent)))


if __name__ == "__main__":
    sys.exit(main())
