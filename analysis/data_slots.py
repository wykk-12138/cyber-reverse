"""What are the 278 non-function vtable slots pointing at -- and do they lead to more functions? (R648)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R636-R647.

**Method, stated before measuring** (R647's lesson: do not measure an authoritative field with a proxy):

  * the slot list is read as exactly `_usNumVtableSlots` entries from `+0x18` -- never by finding runs;
  * a slot is classified by where its value lands: `.pdata` function start / another MethodTable header / inside a
    data section / outside the image;
  * for slots landing in a data section, the code then reads **the 8 bytes at that address** to see whether it is
    itself a function pointer. That is the only way to tell whether the slot is a **one-level indirection** to a
    function (which would add to coverage) or a pointer to unrelated data.

**Verdict rule, fixed before measuring**:

  * **INDIRECTION** -- >= 50% of the data slots point at a qword that is a `.pdata` function start: coverage must be
    recomputed one level deeper.
  * **NOT INDIRECTION** -- that share is below 20%: the 278 slots do not extend coverage and 1,743 stands.

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


def which_section(sections, rva):
    for s in sections:
        if s["vaddr"] <= rva < s["vaddr"] + s["vsize"]:
            return s["name"]
    return None


def main():
    data = open(PATH, "rb").read()
    image_base, dirs_off, sections = parse_pe(data)

    exc_rva, exc_size = struct.unpack_from("<II", data, dirs_off + 3 * 8)
    off = rva_to_off(sections, exc_rva)
    starts = {struct.unpack_from("<I", data, off + i * 12)[0] for i in range(exc_size // 12)}
    starts.discard(0)

    # MethodTable candidates: a run of function pointers whose base-0x18 is referenced somewhere
    tables = []
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        cur = 0
        at = 0
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            rva = va - image_base if va >= image_base else None
            if rva is not None and rva in starts:
                if cur == 0:
                    at = s["vaddr"] + i * 8
                cur += 1
            else:
                if cur >= MIN_RUN:
                    tables.append(at)
                cur = 0
        if cur >= MIN_RUN:
            tables.append(at)

    values = set()
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            if va >= image_base:
                values.add(va - image_base)

    heads = [a - HEADER for a in tables if (a - HEADER) in values]
    head_set = set(heads)
    print("MethodTables: %d" % len(heads))

    kind = Counter()
    where = Counter()
    indirect_fns = set()
    data_slots = 0

    for h in heads:
        o = rva_to_off(sections, h)
        if o is None:
            continue
        slots = struct.unpack_from("<H", data, o + 16)[0]
        for i in range(slots):
            raw = struct.unpack_from("<Q", data, o + 24 + i * 8)[0]
            if raw == 0:
                kind["null"] += 1
                continue
            if raw < image_base:
                kind["below image base"] += 1
                continue
            rva = raw - image_base
            if rva in starts:
                kind["function start"] += 1
                continue
            if rva in head_set:
                kind["another MethodTable"] += 1
                continue
            sec = which_section(sections, rva)
            if sec is None:
                kind["outside image"] += 1
                continue
            kind["data (%s)" % sec] += 1
            where[sec] += 1
            data_slots += 1
            # one level down: is the qword at that address a function start?
            o2 = rva_to_off(sections, rva)
            if o2 is not None and o2 + 8 <= len(data):
                inner = struct.unpack_from("<Q", data, o2)[0]
                if inner >= image_base and (inner - image_base) in starts:
                    indirect_fns.add(inner - image_base)

    print()
    print("slot classification (declared counts, no run detection):")
    for k, v in kind.most_common():
        print("  %-24s %6d" % (k, v))

    print()
    print("data slots: %d   sections: %s" % (data_slots, dict(where)))
    print("of those, the qword at the target is a function start: %d distinct functions" % len(indirect_fns))

    share = (len(indirect_fns) / data_slots) if data_slots else 0.0
    print("share of data slots that lead to a function: %.1f%%" % (100 * share))

    print()
    if share >= 0.50:
        print("VERDICT: INDIRECTION -- coverage must be recomputed one level deeper")
    elif share < 0.20:
        print("VERDICT: NOT INDIRECTION -- the %d data slots do not extend coverage; 1,743 stands" % data_slots)
    else:
        print("VERDICT: PARTIAL INDIRECTION (%.1f%%) -- reported, not generalised" % (100 * share))


if __name__ == "__main__":
    sys.exit(main())
