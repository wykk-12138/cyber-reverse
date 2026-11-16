"""Which functions are byte-identical across 5.18.32 and 5.18.35? (R726)

**Why this exists** (project convention §1.2): `pe_diff.py` compares two builds at header and section level and says so
in its own docstring -- it has no function matching. `analysis/pdata_unwind.py` already parses `.pdata`, so its
`parse_pe` / `rva_to_off` are imported rather than rewritten.

**Why ask this at all.** C7c wants witnesses for "every function behaves the same", and the original cannot be run.
A release delta is the one external fact available: functions a real version bump did not touch are the stable core,
and functions it did touch are version-specific logic that makes a poor witness. This does not prove behaviour -- the
docstring of `pe_diff.py` is right that identical bytes do not prove identical behaviour -- it ranks candidates.

**Ceiling first, before measuring** (R644's rule):
  * `.pdata` holds one RUNTIME_FUNCTION per non-leaf function: 277,094 of IDA's 321,244 = **86.2%**.
  * Leaf functions carry no unwind entry and are therefore invisible here. Everything below is about that 86.2%.

**What is measured**: SHA-256 of each function's bytes in each image, then a multiset comparison. A hash present in both
is a function whose body did not change; a hash unique to one image is new or rewritten. Same-size-and-same-bytes is the
strongest identity available without symbols.
"""

import hashlib
import io
import os
import struct
import sys
from collections import Counter

sys.path.insert(0, os.path.join(r"D:\projects\cyber-reverse", "analysis"))
import pdata_unwind as P

A = r"D:\projects\cyber-reverse\target\Cybersole.exe"
B = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Cybersole", "current", "Cybersole.exe")
OUT = r"D:\projects\cyber-reverse\analysis\function_stability.txt"


def functions(path):
    """(sections, [(begin_rva, end_rva)]) from .pdata."""
    data = open(path, "rb").read()
    _image_base, _dirs_off, sections = P.parse_pe(data)
    pdata = None
    for s in sections:
        if s.get("name") == ".pdata":
            pdata = s
            break
    if pdata is None:
        return sections, []
    off = pdata["rawptr"]
    size = pdata["rawsize"]
    out = []
    for i in range(0, size - 11, 12):
        begin, end, _unwind = struct.unpack_from("<III", data, off + i)
        if begin and end and end > begin:
            out.append((begin, end))
    return sections, out


def _mask(body, lo, hi):
    """Zero every 4-byte aligned word that reads as an address inside the image.

    Without this the comparison is dominated by relayout: NativeAOT embeds RVAs and image addresses inside
    function bodies, so a whole-image shift rewrites bytes in functions whose logic did not change. The raw
    number (25.1% identical) therefore says more about layout than about edits. Masking removes that noise;
    what is left is the part that cannot be explained by a moved reference.
    """
    b = bytearray(body)
    for i in range(0, len(b) - 3, 4):
        v = int.from_bytes(b[i:i + 4], "little")
        if lo <= v < hi:
            b[i:i + 4] = b"\0\0\0\0"
    return bytes(b)


def hashes(path, sections, ranges, mask=False):
    data = open(path, "rb").read()
    lo, hi = 0, 0
    if mask:
        lo = min(s["vaddr"] for s in sections)
        hi = max(s["vaddr"] + max(s["vsize"], s["rawsize"]) for s in sections)
    out = []
    for begin, end in ranges:
        bo = P.rva_to_off(sections, begin)
        eo = P.rva_to_off(sections, end)
        if bo is None or eo is None or eo <= bo:
            continue
        body = data[bo:eo]
        if mask:
            body = _mask(body, lo, hi)
        out.append(hashlib.sha256(body).hexdigest())
    return out


def main():
    for p in (A, B):
        if not os.path.exists(p):
            print("missing: %s" % p)
            return 1

    sa, ra = functions(A)
    sb, rb = functions(B)
    print("5.18.32  .pdata entries : %d" % len(ra))
    print("5.18.35  .pdata entries : %d" % len(rb))

    ha = Counter(hashes(A, sa, ra))
    hb = Counter(hashes(B, sb, rb))
    print("hashed                  : %d / %d" % (sum(ha.values()), sum(hb.values())))

    both = ha & hb
    only_a = ha - hb
    only_b = hb - ha
    n_both = sum(both.values())
    print()
    print("identical in both       : %d" % n_both)
    print("only in 5.18.32         : %d" % sum(only_a.values()))
    print("only in 5.18.35         : %d" % sum(only_b.values()))
    total = sum(ha.values())
    if total:
        print("stable share            : %.1f%%" % (100.0 * n_both / total))

    # a function can keep its address and still change; check positional identity too
    same_pos = 0
    for i in range(min(len(ra), len(rb))):
        if ra[i][0] == rb[i][0] and ra[i][1] == rb[i][1]:
            same_pos += 1
    print()
    print("same RVA range at the same index : %d of %d (%.1f%%)"
          % (same_pos, min(len(ra), len(rb)), 100.0 * same_pos / max(min(len(ra), len(rb)), 1)))

    # the same comparison with in-body addresses masked out
    ma = Counter(hashes(A, sa, ra, mask=True))
    mb = Counter(hashes(B, sb, rb, mask=True))
    m_both = sum((ma & mb).values())
    m_only_a = sum((ma - mb).values())
    m_only_b = sum((mb - ma).values())
    print()
    print("[masked] identical in both : %d (%.1f%%)" % (m_both, 100.0 * m_both / max(sum(ma.values()), 1)))
    print("[masked] only in 5.18.32   : %d" % m_only_a)
    print("[masked] only in 5.18.35   : %d" % m_only_b)

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# 5.18.32 vs 5.18.35 function stability (R726)\n")
        fh.write("pdata_32\t%d\npdata_35\t%d\n" % (len(ra), len(rb)))
        fh.write("identical\t%d\nonly_32\t%d\nonly_35\t%d\n"
                 % (n_both, sum(only_a.values()), sum(only_b.values())))
        fh.write("masked_identical\t%d\nmasked_only_32\t%d\nmasked_only_35\t%d\n"
                 % (m_both, m_only_a, m_only_b))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
