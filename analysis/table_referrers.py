"""Does anything reference the 852 vtable-shaped tables? The falsifiable test for B-class #2. (R638)

**Why this exists** (project convention §1.2): R636 recorded why the IDA database could not be opened this session
(1.7-2.4 GB free against a 1.4 GB `.i64`). This is the same file-only route, and it is deliberately a **falsifiable**
test -- if nothing points at the tables, the candidate entry point recorded in R637 is wrong and must be withdrawn.

**The question**: R637 found 852 tables of >= 32 entries that are vtable-shaped (all entries distinct, mostly
non-monotonic). AOT type metadata would hold a **handle** to such a table -- typically a pointer to its first slot.
So: do any 8-byte values in the data sections equal one of those 852 addresses?

Both encodings are checked, because the image has a `.reloc` section (so absolute addresses are plausible) and an
RVA-only encoding is also common in AOT metadata:

  * **VA form**: qword == image_base + table_rva
  * **RVA form**: dword == table_rva

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
    print("function starts: %d" % len(starts))

    # rebuild the >= MIN_RUN tables (same rule as R637)
    tables = []
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        n = len(body) // 8
        cur = 0
        run_at = 0
        for i in range(n):
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

    table_rvas = {t[0] for t in tables}
    print("tables >= %d: %d" % (MIN_RUN, len(tables)))

    # scan every data section for VA-form and RVA-form references
    va_hits = Counter()
    rva_hits = Counter()
    va_ref_count = 0
    rva_ref_count = 0
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            if va < image_base:
                continue
            rva = va - image_base
            if rva in table_rvas:
                va_hits[s["name"]] += 1
                va_ref_count += 1
        for i in range(len(body) // 4):
            d = struct.unpack_from("<I", body, i * 4)[0]
            if d in table_rvas:
                rva_hits[s["name"]] += 1
                rva_ref_count += 1

    referenced = set()
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            if va >= image_base and (va - image_base) in table_rvas:
                referenced.add(va - image_base)

    print()
    print("VA-form references (qword == base + table_rva):")
    print("  total              : %d" % va_ref_count)
    print("  by section         : %s" % dict(va_hits))
    print("  tables referenced  : %d / %d" % (len(referenced), len(tables)))

    print()
    print("RVA-form references (dword == table_rva):")
    print("  total              : %d" % rva_ref_count)
    print("  by section         : %s" % dict(rva_hits))

    print()
    if va_ref_count == 0 and rva_ref_count == 0:
        print("VERDICT: nothing references the tables -- the R637 candidate entry point is WITHDRAWN")
    elif va_ref_count:
        print("VERDICT: tables are referenced (%d VA refs over %d tables) -- the candidate entry point survives"
              % (va_ref_count, len(referenced)))
    else:
        print("VERDICT: only RVA-form hits (%d) -- weaker evidence, needs a second check" % rva_ref_count)


if __name__ == "__main__":
    sys.exit(main())
