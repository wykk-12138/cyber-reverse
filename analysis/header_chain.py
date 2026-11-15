"""Follow slot 1: do the headers form a chain, and is slot 2 an index? (R639b)

R639's classifier had a bug worth recording: it treated "not inside any section" (`?`) as if it were a section name, so
two packed non-address slots scored `top-section = ? 100%` and were labelled POINTER. Under the rule as written before
measuring -- "at least 90% of the slot's values fall inside **one section's address range**" -- `?` does not qualify.
Corrected reading: slot 1 is a pointer, slots 0 and 2 are not.

The values themselves suggested two concrete structures, and this checks both rather than asserting them:

  1. **slot 1 forms a chain**: e.g. header 0x04B5B968 has slot 1 = 0x144B5B598, which is header 0x04B5B598 -- i.e. it
     points at the *previous* header. Test: for each header, is slot 1 in the header set? Is it the previous header in
     address order?
  2. **slot 2 carries an index**: low 16 bits read 0x0024, 0x0025, 0x0035 in address order. Test: is the sequence
     monotonic, and does it increment by a constant?

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

    # --- test 1: slot 1 chain
    into_headers = 0
    into_previous = 0
    targets = Counter()
    for idx, (h, _c, q) in enumerate(heads):
        v = q[1]
        if v < image_base:
            continue
        rva = v - image_base
        targets["header" if rva in head_set else "other"] += 1
        if rva in head_set:
            into_headers += 1
            if idx > 0 and rva == heads[idx - 1][0]:
                into_previous += 1

    print()
    print("test 1 -- slot 1 target kind:")
    print("  points into the header set : %d / %d" % (into_headers, len(heads)))
    print("  points at the PREVIOUS header in address order: %d" % into_previous)
    print("  target kinds               : %s" % dict(targets))

    # --- test 2: slot 2 low 16 bits as an index
    lows = [q[2] & 0xFFFF for _h, _c, q in heads]
    highers = [q[2] >> 16 for _h, _c, q in heads]
    monotonic = all(lows[i] <= lows[i + 1] for i in range(len(lows) - 1))
    deltas = Counter(lows[i + 1] - lows[i] for i in range(len(lows) - 1))
    print()
    print("test 2 -- slot 2 low 16 bits:")
    print("  first 12 : %s" % lows[:12])
    print("  monotonic non-decreasing : %s" % monotonic)
    print("  distinct values          : %d / %d" % (len(set(lows)), len(lows)))
    print("  delta histogram (top 5)  : %s" % deltas.most_common(5))
    print("  middle 16 bits distinct  : %d" % len(set((q[2] >> 16) & 0xFFFF for _h, _c, q in heads)))
    print("  high 32 bits distinct    : %d" % len(set(highers)))

    # --- control: slot 0 low 16 bits
    l0 = [q[0] & 0xFFFF for _h, _c, q in heads]
    print()
    print("slot 0 low 16 bits: distinct=%d  sample=%s" % (len(set(l0)), l0[:8]))


if __name__ == "__main__":
    sys.exit(main())
