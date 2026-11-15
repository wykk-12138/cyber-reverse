"""Alt hypothesis for R638: are the tables referenced by an INTERIOR slot rather than by their first slot? (R638b)

R638 found zero references to any of the 852 table bases, in both VA and RVA encodings. Before withdrawing the R637
candidate entry point, the obvious alternative must be ruled out: a type handle usually points at the **start** of a
vtable, but a `base + k` handle (interface offset, generic instantiation) would point inside it.

So this repeats the scan against **every slot address** of every table, not just the base. If interior references
exist, the tables are still reachable and the entry point survives in a weaker form; if there are none either, the
withdrawal is solid.

Read-only. Prints; writes nothing.
"""

import struct
import sys
from collections import Counter

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"
MIN_RUN = 32


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

    # every slot address of every table
    slots = set()
    for base, count in tables:
        for k in range(count):
            slots.add(base + k * 8)

    print("tables >= %d : %d" % (MIN_RUN, len(tables)))
    print("total slots  : %d" % len(slots))

    va_hits = Counter()
    per_table = Counter()
    slot_owner = {}
    for base, count in tables:
        for k in range(count):
            slot_owner[base + k * 8] = base

    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            if va < image_base:
                continue
            rva = va - image_base
            if rva in slots:
                va_hits[s["name"]] += 1
                per_table[slot_owner[rva]] += 1

    total = sum(va_hits.values())
    print()
    print("references to ANY slot (VA form):")
    print("  total            : %d" % total)
    print("  by section       : %s" % dict(va_hits))
    print("  distinct tables pointed into: %d / %d" % (len(per_table), len(tables)))

    print()
    if total == 0:
        print("VERDICT: no reference to any slot either -- R637 entry point stays WITHDRAWN")
    else:
        print("VERDICT: interior references exist -- entry point survives in a weaker (base+k) form")
        for base, n in per_table.most_common(5):
            print("   table 0x%08X referenced %d time(s)" % (base, n))


if __name__ == "__main__":
    sys.exit(main())
