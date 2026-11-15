"""Alt hypothesis 2 for R638: the pointer lands on a header JUST BEFORE the table (inline-vtable MethodTable). (R638c)

R638 found zero references to the 852 tables' bases, and R638b found zero to any slot. A vtable that nothing points at
cannot be a vtable -- **unless the pointer names a structure whose slots start a little later**. NativeAOT lays out a
`MethodTable` header and then the vtable slots inline, so a reference to the type would land at `table_base - k` for a
small k.

This scans a window `[base - WINDOW, base - 8]` for each table and reports:

  * how many tables have such a reference,
  * the **distribution of k = base - referenced_address**, which is the header size if the hypothesis holds.

A single dominant k is a strong structural finding: it turns "852 unreferenced tables" into "852 type structures with
a header of known size", which is exactly what modelling needs.

Read-only. Prints; writes nothing.
"""

import struct
import sys
from collections import Counter

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"
MIN_RUN = 32
WINDOW = 0x100


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

    print("tables >= %d: %d" % (MIN_RUN, len(tables)))

    # every qword in the data sections, as RVAs
    values = set()
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            if va >= image_base:
                values.add(va - image_base)
    print("distinct qword targets in data sections: %d" % len(values))

    k_hist = Counter()
    hit_tables = 0
    first_samples = []
    for base, count in tables:
        found = None
        for k in range(8, WINDOW + 1, 8):
            if base - k in values:
                found = k
                break
        if found is not None:
            hit_tables += 1
            k_hist[found] += 1
            if len(first_samples) < 6:
                first_samples.append((base, found, count))

    print()
    print("tables with a reference in [base-%d, base-8]: %d / %d" % (WINDOW, hit_tables, len(tables)))
    if k_hist:
        print("  k = base - referenced (header size candidates):")
        for k, n in k_hist.most_common(8):
            print("    k=0x%03X (%3d)  x%d" % (k, k, n))
        print("  samples:")
        for base, k, count in first_samples:
            print("    table 0x%08X n=%-4d referenced at base-0x%X" % (base, count, k))
    else:
        print("  none -- the inline-header hypothesis does not hold either")

    print()
    if hit_tables == 0:
        print("VERDICT: neither base, slot, nor a nearby header is referenced -- tables are data-orphaned")
    else:
        top_k, top_n = k_hist.most_common(1)[0]
        print("VERDICT: %d tables have a nearby header reference; dominant k=0x%X covers %d of them"
              % (hit_tables, top_k, top_n))


if __name__ == "__main__":
    sys.exit(main())
