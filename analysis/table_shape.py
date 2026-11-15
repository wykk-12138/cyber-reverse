"""What shape are the long pointer tables? Step and target pattern, from the PE only. (R637)

**Why this exists** (project convention §1.2): the natural tool would be IDA, and R636 explained why the database could
not be opened -- the machine was down to 1.7-2.4 GB free. This continues the same file-only route, reusing the
`.pdata` function-start set as the authority for "this qword points at a function".

**What it asks**, per table: are the targets *regular*?

  * targets strictly increasing with a small constant delta  -> a **jump table** (switch) whose entries are functions
  * targets interleaved / non-monotonic                     -> a **vtable-like slot layout**
  * targets unrelated                                       -> an unrelated **delegate / callback array**

A jump table's targets are *basic blocks*, not function entries, so they cannot appear in a run built from function
starts at all. That is worth stating up front: **every run measured here is a table of function entries by
construction**, and the question is only whether the entries are ordered.

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
    (_machine, nsect, _t, _d, _p, opt_size, _c) = struct.unpack_from("<HHIIIHH", data, coff)
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
    starts = set()
    for i in range(exc_size // 12):
        begin = struct.unpack_from("<I", data, off + i * 12)[0]
        if begin:
            starts.add(begin)
    print("function starts (.pdata): %d" % len(starts))

    # collect runs >= MIN_RUN with their target lists
    tables = []
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        cur = []
        base_rva = s["vaddr"]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            rva = va - image_base if va >= image_base else None
            if rva is not None and rva in starts:
                cur.append(rva)
            else:
                if len(cur) >= MIN_RUN:
                    tables.append((s["name"], base_rva + (i - len(cur)) * 8, list(cur)))
                cur = []
        if len(cur) >= MIN_RUN:
            tables.append((s["name"], base_rva + (len(body) // 8 - len(cur)) * 8, list(cur)))

    print("tables with >= %d entries: %d" % (MIN_RUN, len(tables)))
    print()

    increasing = 0
    constant_delta = 0
    non_monotonic = 0
    delta_hist = Counter()

    for _name, _at, targets in tables:
        diffs = [targets[i + 1] - targets[i] for i in range(len(targets) - 1)]
        if all(d > 0 for d in diffs):
            increasing += 1
        else:
            non_monotonic += 1
        if diffs and len(set(diffs)) == 1:
            constant_delta += 1
            delta_hist[diffs[0]] += 1

    print("target order across %d tables:" % len(tables))
    print("  strictly increasing : %d" % increasing)
    print("  non-monotonic       : %d" % non_monotonic)
    print("  constant delta      : %d" % constant_delta)
    if delta_hist:
        print("  constant deltas seen: %s" % dict(list(delta_hist.items())[:6]))

    tables.sort(key=lambda t: -len(t[2]))
    print()
    print("longest 8 tables:")
    for name, at, targets in tables[:8]:
        diffs = [targets[i + 1] - targets[i] for i in range(len(targets) - 1)]
        mono = all(d > 0 for d in diffs)
        print("  %-7s @0x%08X  n=%-5d mono=%-5s  first=0x%08X  distinct=%d"
              % (name, at, len(targets), mono, targets[0], len(set(targets))))
        print("        deltas: min=%d max=%d  sample=%s"
              % (min(diffs), max(diffs), diffs[:6]))

    # a vtable signature: every target distinct and no ordering
    all_distinct = sum(1 for _n, _a, t in tables if len(set(t)) == len(t))
    print()
    print("tables whose entries are all distinct: %d / %d" % (all_distinct, len(tables)))

    # how much of .text do these tables touch
    touched = set()
    for _n, _a, t in tables:
        touched.update(t)
    print("distinct functions referenced by these tables: %d" % len(touched))
    print("as a share of all .pdata starts: %.1f%%" % (100.0 * len(touched) / len(starts)))


if __name__ == "__main__":
    sys.exit(main())
