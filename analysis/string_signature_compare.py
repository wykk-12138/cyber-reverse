"""Compare 5.18.32 and 5.18.35 by which string CONTENTS each function references. (R728)

**Why this exists** (project convention §1.2): R726 measured that byte-level function hashing returns 25.1% identity
across the two builds and that masking in-image addresses lifts it only to 29.4%, because the dominant cause is
`lea [rip+disp32]` -- after relayout the displacement becomes a different small number that no address mask catches.
`pe_diff.py` is section-level, and `rea`'s `match_native_functions` states in its own documentation that "relocations
are not normalized", so its byte tier hits the same wall; its CFG/call/string fingerprint tier would work but needs two
129 MB NativeAOT images opened in a provider, which is not a one-round cost.

So this is the cheap, relocation-invariant approximation that R727 verified is feasible: extract every string with its
address from raw bytes (no IDA), scan `.text` for displacements resolving to those addresses, attribute each hit to its
function through `.pdata`, and compare the resulting **sets of referenced string contents**.

**What this proves and what it does not.** Equal signatures mean two functions mention the same strings; they can still
order, test and combine them differently. Different signatures mean at least one function references a string the other
does not, which is not explainable by relayout. So equality is necessary-not-sufficient and difference is informative.
A high identical share means relayout noise has been removed; it does not mean behaviour is equal.

**Ceiling, stated before measuring** (R644's rule):
  * `.pdata` covers 277,094 of IDA's 321,244 functions = 86.2%; leaf functions are invisible.
  * A function with no string reference at all has an empty signature, and every such function looks identical to
    every other. Those are counted separately, because collapsing them would inflate the identical share.
"""

import hashlib
import io
import os
import re
import struct
import sys
from bisect import bisect_right
from collections import Counter

sys.path.insert(0, os.path.join(r"D:\projects\cyber-reverse", "analysis"))
import pdata_unwind as P
import disp32_scan_any as D

A = r"D:\projects\cyber-reverse\target\Cybersole.exe"
B = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Cybersole", "current", "Cybersole.exe")
OUT = r"D:\projects\cyber-reverse\analysis\string_signature_compare.txt"

ASCII_RUN = re.compile(rb"[\x20-\x7e]{6,}")
UTF16_RUN = re.compile(rb"(?:[\x20-\x7e]\x00){6,}")


def image(path):
    data = open(path, "rb").read()
    _base, _dirs, sections = P.parse_pe(data)
    return data, sections


def functions(sections_src, data):
    pd = next((s for s in sections_src if s["name"] == ".pdata"), None)
    out = []
    if pd:
        for i in range(0, pd["rawsize"] - 11, 12):
            begin, end, _u = struct.unpack_from("<III", data, pd["rawptr"] + i)
            if begin and end > begin:
                out.append((begin, end))
    out.sort()
    return out


def off_to_rva(sections, off):
    for s in sections:
        if s["rawptr"] <= off < s["rawptr"] + s["rawsize"]:
            return s["vaddr"] + (off - s["rawptr"])
    return None


def strings_with_va(data, sections):
    """{va: sha1 of content}. The frozen-object header sits 12 bytes before the chars for wide literals, but a
    displacement can point at either; both offsets are registered and resolve to the same content hash."""
    out = {}
    for m in ASCII_RUN.finditer(data):
        rva = off_to_rva(sections, m.start())
        if rva is not None:
            out[rva] = hashlib.sha1(m.group()).hexdigest()
    for m in UTF16_RUN.finditer(data):
        rva = off_to_rva(sections, m.start())
        if rva is not None:
            out[rva] = hashlib.sha1(m.group()).hexdigest()
            out[rva - 12] = hashlib.sha1(m.group()).hexdigest()
    return out


def signatures(path):
    data, sections = image(path)
    funcs = functions(sections, data)
    starts = [f[0] for f in funcs]
    table = strings_with_va(data, sections)
    if not table:
        return funcs, Counter()

    # the scanner works in VA space; strings_with_va is RVA space
    base = 0x140000000
    targets = {va + base for va in table}
    hits = D.scan(data, targets)

    per_func = {}
    for tgt, sites in hits.items():
        content = table.get(tgt - base)
        if content is None:
            continue
        for site in sites:
            # D.scan reports FILE OFFSETS. TEXT_VA - TEXT_OFF turns one into a VA, and .pdata begin/end are
            # RVAs, so the image base has to come back off before the bisect. (R728: the first version named
            # the result `rva` while it held a VA, so every lookup landed past the last function and the
            # comparison reported 0 non-empty signatures for both images.)
            va = site + D.TEXT_VA - D.TEXT_OFF
            rva = va - base
            i = bisect_right(starts, rva) - 1
            if i < 0:
                continue
            begin, end = funcs[i]
            if rva < end:
                per_func.setdefault(begin, set()).add(content)

    sigs = Counter()
    for begin, _end in funcs:
        s = per_func.get(begin)
        if not s:
            sigs["EMPTY"] += 1
        else:
            sigs[hashlib.sha1(("|".join(sorted(s))).encode()).hexdigest()] += 1
    return funcs, sigs


def main():
    for p in (A, B):
        if not os.path.exists(p):
            print("missing: %s" % p)
            return 1

    fa, sa = signatures(A)
    fb, sb = signatures(B)
    print("5.18.32  functions %d   signatures %d  (distinct non-empty %d)"
          % (len(fa), sum(sa.values()), len([k for k in sa if k != "EMPTY"])))
    print("5.18.35  functions %d   signatures %d  (distinct non-empty %d)"
          % (len(fb), sum(sb.values()), len([k for k in sb if k != "EMPTY"])))

    empty_a = sa.get("EMPTY", 0)
    empty_b = sb.get("EMPTY", 0)
    nz_a = {k: v for k, v in sa.items() if k != "EMPTY"}
    nz_b = {k: v for k, v in sb.items() if k != "EMPTY"}
    both = sum((Counter(nz_a) & Counter(nz_b)).values())
    only_a = sum((Counter(nz_a) - Counter(nz_b)).values())
    only_b = sum((Counter(nz_b) - Counter(nz_a)).values())

    print()
    print("no string reference at all : %d / %d   (excluded from the comparison)" % (empty_a, empty_b))
    print("non-empty in both          : %d" % both)
    print("only in 5.18.32            : %d" % only_a)
    print("only in 5.18.35            : %d" % only_b)
    denom = both + only_a
    if denom:
        print("identical share (non-empty): %.1f%%" % (100.0 * both / denom))

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# string-reference signature comparison (R728)\n")
        fh.write("funcs_32\t%d\nfuncs_35\t%d\n" % (len(fa), len(fb)))
        fh.write("empty_32\t%d\nempty_35\t%d\n" % (empty_a, empty_b))
        fh.write("identical\t%d\nonly_32\t%d\nonly_35\t%d\n" % (both, only_a, only_b))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
