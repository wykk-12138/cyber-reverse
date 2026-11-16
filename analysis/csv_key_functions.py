"""Find the functions that reference a given set of locale keys. (R745)

R744 left two gaps that share one question: which function produces `ProfileCsv.Status.NoHeader` and which produces
`ProfileCsv.Status.Imported`? They sit beside the `IgnoredColumns` function R743 read, so scanning for the keys
themselves is more direct than reading neighbours.

**Why not an existing tool** (AGENTS.md §1.2): `xrefs_to` answers about code references to an address, and these are
locale keys inside a packed blob whose characters a `lea` reaches through the frozen-object header twelve bytes earlier
(R703). `analysis/witness_keys.py` already does exactly this for the candidate set; this reuses the same three steps --
find the bytes, scan `.text` for a displacement to the header, attribute through `.pdata` -- with the key list as an
argument instead of a hard-coded candidate file.
"""

import io
import json
import os
import re
import struct
import sys
from bisect import bisect_right
from collections import defaultdict

sys.path.insert(0, os.path.join(r"D:\projects\cyber-reverse", "analysis"))
import pdata_unwind as P
import disp32_scan_any as D

A = r"D:\projects\cyber-reverse\target\Cybersole.exe"
BASE = 0x140000000
KEYS = [
    "ProfileCsv.Status.NoHeader",
    "ProfileCsv.Status.Imported",
    "ProfileCsv.Status.IgnoredColumns",
    "ProfileCsv.Status.ParseFailed",
    "ProfileCsv.Status.Exported",
    "ProfileCsv.Status.Replaced",
    "ProfileCsv.Status.FixErrors",
    "ProfileCsv.Status.RegexInvalid",
    "ProfileCsv.Summary.Edited",
    "ProfileCsv.Summary.Errors",
    "ProfileCsv.Summary.New",
    "ProfileCsv.Summary.Removed",
    "ProfileCsv.Summary.None",
    "ProfileCsv.ConfirmDeleteFormat",
    "ProfileCsv.Menu.SelectedCells",
    "ProfileCsv.Clipboard",
]


def main():
    data = open(A, "rb").read()
    _b, _d, sections = P.parse_pe(data)

    def off_to_rva(off):
        for s in sections:
            if s["rawptr"] <= off < s["rawptr"] + s["rawsize"]:
                return s["vaddr"] + (off - s["rawptr"])
        return None

    # key -> every VA its bytes occur at
    where = defaultdict(list)
    for key in KEYS:
        for enc in (key.encode("ascii", "ignore"), key.encode("utf-16-le")):
            i = data.find(enc)
            n = 0
            while i >= 0 and n < 256:
                rva = off_to_rva(i)
                if rva is not None:
                    where[key].append(rva)
                n += 1
                i = data.find(enc, i + 1)

    located = {k: v for k, v in where.items() if v}
    print("  keys located: %d of %d" % (len(located), len(KEYS)))

    # .pdata function ranges
    pd = next(s for s in sections if s["name"] == ".pdata")
    funcs = []
    for i in range(0, pd["rawsize"] - 11, 12):
        begin, end, _u = struct.unpack_from("<III", data, pd["rawptr"] + i)
        if begin and end > begin:
            funcs.append((begin, end))
    funcs.sort()
    starts = [f[0] for f in funcs]

    rva_to_key = {}
    for k, rvas in located.items():
        for rva in rvas:
            rva_to_key[rva] = k

    targets = {rva + BASE - 12 for rva in rva_to_key}    # the object header sits twelve bytes before the chars
    hits = D.scan(data, targets)

    per_func = defaultdict(set)
    for tgt, sites in hits.items():
        key = rva_to_key.get(tgt - BASE + 12)
        if not key:
            continue
        for site in sites:
            va = site + D.TEXT_VA - D.TEXT_OFF
            rva = va - BASE
            i = bisect_right(starts, rva) - 1
            if i < 0:
                continue
            begin, end = funcs[i]
            if rva < end:
                per_func[begin].add(key)

    print("  distinct functions: %d" % len(per_func))
    print()
    for begin in sorted(per_func):
        size = dict(funcs).get(begin, 0) - begin
        print("  0x%-12x size=%-6d %s" % (begin + BASE, size, ", ".join(sorted(per_func[begin]))[:96]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
