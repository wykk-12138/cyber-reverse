"""Resolve the function-pointer slots the profiles guard calls through. (R738)

`sub_1406E9190` (profiles delete confirmation) exits early on `if (!v4)`, where

    v3 = off_14492E6C8();        // a no-argument call through a slot
    v4 = off_14492E970(v3);      // a lookup taking that result

Neither layer was resolved in R737, so the profiles screen was left unwired. A slot read earlier in R731 came back
with an implausible length because those slots held descriptors, not strings -- but these two are **called**, so their
targets must be code, and a target inside `.text` can be decompiled.

**Why not an existing tool** (AGENTS.md §1.2): `read_bytes` through the plugin returned an empty object for the earlier
slot reads, and `xrefs_to` answers about references to an address rather than about what a data slot holds. The PE
reader in `pdata_unwind.py` is already in use here.
"""

import io
import os
import struct
import sys

sys.path.insert(0, os.path.join(r"D:\projects\cyber-reverse", "analysis"))
import pdata_unwind as P

A = r"D:\projects\cyber-reverse\target\Cybersole.exe"
SLOTS = ["0x14492E6C8", "0x14492E970"]
BASE = 0x140000000


def main():
    data = open(A, "rb").read()
    _b, _d, sections = P.parse_pe(data)
    text = next(s for s in sections if s["name"] == ".text")
    lo, hi = BASE + text["vaddr"], BASE + text["vaddr"] + text["vsize"]
    print("  .text spans 0x%x .. 0x%x" % (lo, hi))
    print()

    for slot in SLOTS:
        off = P.rva_to_off(sections, int(slot, 16) - BASE)
        if off is None:
            print("  %-14s outside the file" % slot)
            continue
        value = struct.unpack_from("<Q", data, off)[0]
        where = ("code in .text" if lo <= value < hi
                 else "data" if BASE <= value < BASE + len(data)
                 else "not an image pointer")
        print("  %-14s -> 0x%-12x  %s" % (slot, value, where))
        if lo <= value < hi:
            # confirm a function actually starts there
            pd = next(s for s in sections if s["name"] == ".pdata")
            rva = value - BASE
            hit = None
            for i in range(0, pd["rawsize"] - 11, 12):
                begin, end, _u = struct.unpack_from("<III", data, pd["rawptr"] + i)
                if begin == rva:
                    hit = (begin, end)
                    break
            print("       function start: %s" % ("yes, %d bytes" % (hit[1] - hit[0]) if hit
                                                 else "no .pdata entry"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
