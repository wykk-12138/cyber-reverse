"""Are the 7 long (class-B) tables' targets concentrated in one region of .text? (R644)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636). Same file-only
route as R636-R643.

**Why the threshold comes first**: R643's lesson was that a *name* ("vtable region") outran the evidence. "Concentrated"
is the same kind of word -- it sounds like an observation but is a judgement. So it is quantified before any data is
looked at:

  * `.text` is cut into **64 equal-width buckets**.
  * A table set is **CONCENTRATED** when **>= 60% of its distinct targets fall in <= 4 buckets** -- i.e. 6.25% of the
    address space carries 60% of the targets.
  * The **A-class set (363 header-bearing tables) is measured the same way as a control**. If both sets look alike,
    "concentration" says nothing about class B specifically.

Targets here are the table entries themselves (function addresses), not the tables' bases.

Read-only. Prints; writes nothing.
"""

import struct
import sys
from collections import Counter

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"
MIN_RUN = 32
HEADER = 0x18
BUCKETS = 64
LONG = 80


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


def collect(sections, image_base, starts):
    """Return [(table_base, length, [targets...])] for every run of >= MIN_RUN function pointers."""
    out = []
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data_slice(s)
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
                    out.append((at, len(cur), list(cur)))
                cur = []
        if len(cur) >= MIN_RUN:
            out.append((at, len(cur), list(cur)))
    return out


def data_slice(s):
    return GLOBAL_DATA[s["rawptr"]:s["rawptr"] + s["rawsize"]]


def bucketize(targets, text_lo, text_span):
    c = Counter()
    for t in targets:
        if t < text_lo or t >= text_lo + text_span:
            c["outside .text"] += 1
            continue
        c[(t - text_lo) * BUCKETS // text_span] += 1
    return c


def report(label, table_set, text_lo, text_span):
    all_targets = []
    for _base, _len, targets in table_set:
        all_targets.extend(targets)
    distinct = set(all_targets)
    c = bucketize(distinct, text_lo, text_span)
    top = c.most_common(4)
    covered = sum(n for _k, n in top)
    total = sum(c.values())
    print()
    print("%s: %d tables, %d slots, %d distinct targets" % (label, len(table_set), len(all_targets), len(distinct)))
    print("  top 4 of %d buckets: %s" % (BUCKETS, top))
    print("  covered by top 4: %d / %d = %.1f%%   (threshold for CONCENTRATED: >=60%%)"
          % (covered, total, 100.0 * covered / total if total else 0))
    return covered / total if total else 0.0


GLOBAL_DATA = b""


def main():
    global GLOBAL_DATA
    GLOBAL_DATA = open(PATH, "rb").read()
    data = GLOBAL_DATA
    image_base, dirs_off, sections = parse_pe(data)

    text = next(s for s in sections if s["name"] == ".text")
    text_lo, text_span = text["vaddr"], text["vsize"]

    exc_rva, exc_size = struct.unpack_from("<II", data, dirs_off + 3 * 8)
    off = rva_to_off(sections, exc_rva)
    starts = {struct.unpack_from("<I", data, off + i * 12)[0] for i in range(exc_size // 12)}
    starts.discard(0)

    tables = collect(sections, image_base, starts)

    values = set()
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            if va >= image_base:
                values.add(va - image_base)

    class_a = [t for t in tables if (t[0] - HEADER) in values]
    class_b_long = [t for t in tables if t[0] not in {a[0] for a in class_a} and t[1] > LONG]

    print(".text : rva 0x%08X  size %d  (bucket width %d)" % (text_lo, text_span, text_span // BUCKETS))
    print("tables: %d total, %d class A, %d class B long" % (len(tables), len(class_a), len(class_b_long)))

    a_share = report("CLASS A (363 header-bearing)", class_a, text_lo, text_span)
    b_share = report("CLASS B long (7 tables)", class_b_long, text_lo, text_span)

    print()
    a_conc = a_share >= 0.60
    b_conc = b_share >= 0.60
    if b_conc and not a_conc:
        print("VERDICT: class B long is CONCENTRATED and class A is not -- the two classes differ in target locality")
    elif b_conc and a_conc:
        print("VERDICT: both CONCENTRATED -- the control looks the same, so concentration says nothing about class B")
    elif not b_conc:
        print("VERDICT: class B long is NOT concentrated (%.1f%% in top 4 buckets)" % (100 * b_share))


if __name__ == "__main__":
    sys.exit(main())
