"""Verify the NativeAOT MethodTable layout against the 363 measured headers. (R646)

**Why this exists** (project convention §1.2): the layout comes from the authoritative source, not from my guessing --
`src/coreclr/nativeaot/Common/src/Internal/Runtime/MethodTable.cs` in dotnet/runtime. This script only checks whether
the measured data agrees with it. The IDA database still cannot be opened (R636).

**The documented layout** (64-bit, `[StructLayout(Sequential)]`):

    +0x00  uint   _uFlags          upper ushort = Flags, lower ushort = component size / type-arg count / ExtendedFlags
    +0x04  uint   _uBaseSize
    +0x08  ptr    _relatedType     _pBaseType for canonical types, _pRelatedParameterType otherwise
    +0x10  ushort _usNumVtableSlots
    +0x12  ushort _usNumInterfaces
    +0x14  uint   _uHashCode
    +0x18  ---- vtable starts here (GetVTableStartAddress == this + sizeof(MethodTable))

**Predictions, stated before checking** -- each is falsifiable and each would be visible as a mismatch:

  P1  `_usNumVtableSlots` at +0x10 must equal the measured table length (the run of function pointers at +0x18).
  P2  `_pBaseType` at +0x08 must point at another one of the 363 headers (the class hierarchy R640 saw as components).
  P3  the low ushort of `_uFlags` must be 0 for ordinary classes (non-zero only for strings/arrays).
  P4  `_uHashCode` at +0x14 must be distinct per type.

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
                flags, basesize = struct.unpack_from("<II", data, o)
                related = struct.unpack_from("<Q", data, o + 8)[0]
                slots, ifaces = struct.unpack_from("<HH", data, o + 16)
                hashcode = struct.unpack_from("<I", data, o + 20)
                heads.append((h, count, flags, basesize, related, slots, ifaces, hashcode))

    head_set = {h for h, *_ in heads}
    print("headers: %d" % len(heads))

    # P1 -- slot count equals the measured table length
    p1 = sum(1 for _h, count, _f, _bs, _r, slots, _i, _hc in heads if slots == count)
    print()
    print("P1  _usNumVtableSlots == measured length : %d / %d = %.1f%%"
          % (p1, len(heads), 100.0 * p1 / len(heads)))
    wrong = [(h, count, slots) for h, count, _f, _bs, _r, slots, _i, _hc in heads if slots != count]
    if wrong:
        print("    mismatches (first 5): %s" % [(hex(h), c, s) for h, c, s in wrong[:5]])

    # P2 -- base type points into the header set
    p2 = 0
    outside = 0
    null_base = 0
    for _h, _c, _f, _bs, related, _s, _i, _hc in heads:
        if related == 0:
            null_base += 1
            continue
        rva = related - image_base if related >= image_base else None
        if rva is not None and rva in head_set:
            p2 += 1
        else:
            outside += 1
    print()
    print("P2  _pBaseType -> another header         : %d   outside: %d   null: %d"
          % (p2, outside, null_base))

    # P3 -- component size (low ushort of _uFlags) is 0 for ordinary classes
    lows = Counter(f & 0xFFFF for _h, _c, f, _bs, _r, _s, _i, _hc in heads)
    print()
    print("P3  low ushort of _uFlags (component size): %s" % dict(lows.most_common(6)))

    # P4 -- hash code distinct
    hc = [x[7] for x in heads]
    print()
    print("P4  _uHashCode distinct                  : %d / %d" % (len(set(hc)), len(hc)))

    # bonus -- base size sanity
    sizes = sorted(x[3] for x in heads)
    print()
    print("    _uBaseSize  min %d  median %d  max %d" % (sizes[0], sizes[len(sizes) // 2], sizes[-1]))

    print()
    ok = p1 == len(heads) and len(set(hc)) == len(hc) and lows.most_common(1)[0][0] == 0
    print("VERDICT: %s" % ("layout CONFIRMED on this image" if ok else "layout partially matches -- see mismatches above"))


if __name__ == "__main__":
    sys.exit(main())
