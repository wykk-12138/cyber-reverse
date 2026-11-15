"""Why do 83 tables run longer than `_usNumVtableSlots` says? Read the slots past the declared count. (R647)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R636-R646.

**The question**: for 280 of 363 MethodTables the run length equals `_usNumVtableSlots`; for 83 it runs 1-10 entries
longer. R646 tested the interface-map explanation (`measured == slots + interfaces`) and falsified it at 2.8%.

**What is read now**: for a few mismatching tables, every slot from +0x18 onward, split at the declared count. Two
readings are possible and this decides between them:

  * the extra entries are **a continuation of the same vtable** (same code region as slots 0..n-1), or
  * the extra entries **belong to a different structure** (a different region, or a different pattern).

Extra evidence: whether the entry right after the declared count is also the base of the *next* MethodTable in address
order, which would mean the run simply ran into the neighbour.

Read-only. Prints; writes nothing.
"""

import struct
import sys

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"
MIN_RUN = 32
HEADER = 0x18
SAMPLES = 4


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

    text = next(s for s in sections if s["name"] == ".text")
    text_lo, text_hi = text["vaddr"], text["vaddr"] + text["vsize"]

    exc_rva, exc_size = struct.unpack_from("<II", data, dirs_off + 3 * 8)
    off = rva_to_off(sections, exc_rva)
    starts = {struct.unpack_from("<I", data, off + i * 12)[0] for i in range(exc_size // 12)}
    starts.discard(0)

    tables = []
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        cur = []
        at = 0
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            rva = va - image_base if va >= image_base else None
            if rva is not None and rva in starts:
                if not cur:
                    at = s["vaddr"] + i * 8
                cur.append(rva)
            else:
                if len(cur) >= MIN_RUN:
                    tables.append((at, list(cur)))
                cur = []
        if len(cur) >= MIN_RUN:
            tables.append((at, list(cur)))

    values = set()
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            if va >= image_base:
                values.add(va - image_base)

    bad = []
    for base, targets in tables:
        h = base - HEADER
        if h not in values:
            continue
        o = rva_to_off(sections, h)
        if o is None:
            continue
        slots, ifaces = struct.unpack_from("<HH", data, o + 16)
        if len(targets) != slots:
            bad.append((h, base, slots, ifaces, targets))

    print("mismatching tables: %d" % len(bad))
    print()

    for h, base, slots, ifaces, targets in bad[:SAMPLES]:
        print("MethodTable 0x%08X  declared slots %d  interfaces %d  run %d  (extra %d)"
              % (h, slots, ifaces, len(targets), len(targets) - slots))
        head = targets[:slots]
        extra = targets[slots:]
        def span(ts):
            if not ts:
                return "-"
            intext = [t for t in ts if text_lo <= t < text_hi]
            if not intext:
                return "none in .text"
            return "0x%08X..0x%08X (%d in .text of %d)" % (min(intext), max(intext), len(intext), len(ts))
        print("   declared slots span : %s" % span(head))
        print("   extra entries       : %s" % [hex(t) for t in extra])
        print("   extra span          : %s" % span(extra))
        print("   extra are function starts: %s" % all(t in starts for t in extra))

        # does the run stop exactly at the next MethodTable's vtable start?
        nxt = [(b2 - HEADER) for b2, _t2 in tables if b2 > base]
        if nxt:
            nearest = min(nxt)
            gap = nearest - base
            print("   next MethodTable vtable start 0x%08X  gap %d bytes (run covers %d bytes)"
                  % (nearest + HEADER, gap, len(targets) * 8))
            print("   run overlaps next vtable: %s" % (len(targets) * 8 > gap))
        print()

    # aggregate: are the extra entries inside .text at all, and do runs overlap the next table?
    overlap = 0
    extra_in_text = 0
    for h, base, slots, ifaces, targets in bad:
        extra = targets[slots:]
        if extra and all(text_lo <= t < text_hi for t in extra):
            extra_in_text += 1
        nxt = [b2 for b2, _t2 in tables if b2 > base]
        if nxt and len(targets) * 8 > (min(nxt) - base):
            overlap += 1
    print("aggregate over %d mismatches:" % len(bad))
    print("  extra entries all inside .text : %d" % extra_in_text)
    print("  run overlaps the next vtable   : %d" % overlap)


if __name__ == "__main__":
    sys.exit(main())
