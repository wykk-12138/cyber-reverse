"""For each witness candidate, print the locale keys it references -- the strings identify the function. (R729)

R728 left 76,547 functions whose string signature is identical across the two builds; intersecting that with the 239
functions that reference app text (R720) gives 129. Picking one and reading 200 lines of pseudocode is not how to
identify it: the locale keys a function loads say what it is for more directly than its prologue does.

**Criterion, fixed before measuring**: a candidate is usable for a probe when its referenced keys name a behaviour --
an error message, a validator, a formatter -- rather than a caption. Captions mean UI wiring (R721); messages mean
logic with an output that can be asserted.
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
LOCALES = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Locales\Cybersole.Locales.en.json"
CAND = r"D:\projects\cyber-reverse\analysis\witness_candidates.txt"
OUT = r"D:\projects\cyber-reverse\analysis\witness_candidate_keys.txt"

ASCII_RUN = re.compile(rb"[\x20-\x7e]{6,}")
UTF16_RUN = re.compile(rb"(?:[\x20-\x7e]\x00){6,}")
BASE = 0x140000000


def off_to_rva(sections, off):
    for s in sections:
        if s["rawptr"] <= off < s["rawptr"] + s["rawsize"]:
            return s["vaddr"] + (off - s["rawptr"])
    return None


def main():
    keys = json.load(io.open(LOCALES, encoding="utf-8"))
    # R729: the binary carries the locale KEY NAMES, not the localized text -- R720's app-string scan matched keys
    # and that is what made it work. Building this as {value: key} gave zero hits, which is the sort of quiet zero
    # that comes from inverting a map rather than from an empty input.
    by_text = {k: k for k in keys if isinstance(k, str)}

    data = open(A, "rb").read()
    _b, _d, sections = P.parse_pe(data)
    pd = next(s for s in sections if s["name"] == ".pdata")
    funcs = []
    for i in range(0, pd["rawsize"] - 11, 12):
        begin, end, _u = struct.unpack_from("<III", data, pd["rawptr"] + i)
        if begin and end > begin:
            funcs.append((begin, end))
    funcs.sort()
    starts = [f[0] for f in funcs]

    # R729: search for each key's encoding directly instead of decoding maximal runs. A maximal run spans several
    # adjacent literals, so its decoded text matches no single key -- that is why the run-based version found zero
    # even after the map direction was fixed. R720's IDA-based scan located 985 of 1142 keys; this must agree.
    text_to_rva = {}
    for key in keys:
        if not isinstance(key, str) or len(key) < 6:
            continue
        for enc in (key.encode("ascii", "ignore"), key.encode("utf-16-le")):
            if not enc:
                continue
            i = data.find(enc)
            seen = 0
            # R729: cap raised from 8. A key can appear many times in a 129 MB image and the code references
            # whichever copy the loader was given; stopping at the eighth occurrence silently excluded those.
            while i >= 0 and seen < 512:
                rva = off_to_rva(sections, i)
                if rva is not None:
                    text_to_rva[rva] = key
                seen += 1
                i = data.find(enc, i + 1)
    print("locale keys located in the image: %d of %d" % (len(set(text_to_rva.values())), len(keys)))

    want = set()
    for line in io.open(CAND, encoding="utf-8"):
        if line.startswith("#"):
            continue
        want.add(int(line.split("\t")[0], 16) - BASE)

    # R729: the displacement points at the frozen object HEADER, twelve bytes before the characters (R703). R720's
    # scanner encoded that as `va - 12`; using the characters address directly reproduces the very zero R703 was
    # written to fix. Targets are headers; a hit maps back by adding twelve.
    targets = {rva + BASE - 12 for rva in text_to_rva}
    hits = D.scan(data, targets)

    per_func = defaultdict(set)
    for tgt, sites in hits.items():
        key = text_to_rva.get(tgt - BASE + 12)
        if not key:
            continue
        for site in sites:
            va = site + D.TEXT_VA - D.TEXT_OFF
            rva = va - BASE
            i = bisect_right(starts, rva) - 1
            if i < 0:
                continue
            begin, end = funcs[i]
            if rva < end and begin in want:
                per_func[begin].add(key)

    print("candidates with at least one locale key: %d of %d" % (len(per_func), len(want)))
    print()
    rows = sorted(per_func.items(), key=lambda kv: -len(kv[1]))
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# witness candidates and the locale keys they load (R729)\n")
        for begin, ks in rows:
            line = "0x%x\t%d\t%s" % (begin + BASE, len(ks), ", ".join(sorted(ks)[:6]))
            print(line[:150])
            fh.write(line + "\n")
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
