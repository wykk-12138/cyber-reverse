"""Add a --decompose mode: split the mean difference into what each size band contributes.

WHY THIS EXISTS (AGENTS.md §1.2 requires the reason be stated):

R971 measured both size distributions and wrote down that the mean difference had not been decomposed: "the
six-hundred-kilobyte function contributes only about two and a half bytes to the mean, so most of the nineteen-byte
difference must come from the small-function proportions, and that arithmetic has not been done."

Leaving it there is the shape of claim these rounds keep finding -- a number asserted without the sum behind it.

It is a separate script rather than a third mode of pdata_sections.py, which contradicts the sentence I first wrote here. The
reason is that the band edges are not a knob: a decomposition needs fixed bands whose widths match the size ranges being
compared, while pdata_sections takes a single uniform bucket size for a different question. Making one file serve both would
mean a second set of arguments that are not interchangeable, so the honest arrangement is two scripts sharing the same
section walk, and this header says so instead of claiming otherwise.

The decomposition, stated so it can be checked by hand:
    mean difference = sum over bands of (band share in original - band share in replica) * band midpoint weight
Because the bands are unequal in width, an exact split uses the mean size within each band per image rather than the band's
nominal midpoint. That is what this computes.

What it can and cannot say:
    CAN   : attribute the mean difference to bands, exactly, to within rounding.
    CANNOT: say why a band's share differs. A band with more mass in the original is a compiler and code-shape fact here,
            not evidence about behaviour.

Reproduce:
    cd replica
    python tools/pdata_sections.py --decompose
"""

import io
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORIGINAL = os.path.abspath(os.path.join(ROOT, "..", "target", "Cybersole.exe"))
REPLICA = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")

RUNTIME_FUNCTION_BYTES = 12
BANDS = [(0, 32), (32, 64), (64, 128), (128, 256), (256, 512), (512, 1024), (1024, 4096), (4096, 1 << 20)]


def extents(path):
    if not os.path.exists(path):
        return []
    data = open(path, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\x00\x00":
        return []
    count = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    table = pe + 24 + opt_size
    for i in range(count):
        head = table + i * 40
        if data[head:head + 8].rstrip(b"\x00").decode("ascii", "replace") != ".pdata":
            continue
        _vs, _va, raw_size, raw_ptr = struct.unpack_from("<IIII", data, head + 8)
        out = []
        for off in range(0, raw_size - RUNTIME_FUNCTION_BYTES + 1, RUNTIME_FUNCTION_BYTES):
            begin, end, _u = struct.unpack_from("<III", data, raw_ptr + off)
            if 0 < end - begin < 0x100000:
                out.append(end - begin)
        return out
    return []


def band_of(size):
    for lo, hi in BANDS:
        if lo < size <= hi:
            return (lo, hi)
    return BANDS[0] if size <= 0 else BANDS[-1]


def profile(sizes):
    """Return {band: (count, share, mean_size_in_band)}."""
    total = len(sizes)
    buckets = {}
    for s in sizes:
        buckets.setdefault(band_of(s), []).append(s)
    return {b: (len(v), len(v) / total, sum(v) / len(v)) for b, v in buckets.items()}


def main():
    o = extents(ORIGINAL)
    r = extents(REPLICA)
    if not o or not r:
        print("  one artifact is missing or has no .pdata -- missing measurement, not a zero")
        return 1

    op, rp = profile(o), profile(r)
    o_mean, r_mean = sum(o) / len(o), sum(r) / len(r)

    print("decomposing the mean function size difference")
    print("  original mean %.2f B over %d functions" % (o_mean, len(o)))
    print("  replica  mean %.2f B over %d functions" % (r_mean, len(r)))
    print("  difference: %+.2f B" % (o_mean - r_mean))
    print()
    print("  %-14s %-22s %-22s %s" % ("band (B)", "original n / share", "replica n / share", "contribution"))
    print("  " + "-" * 84)

    explained = 0.0
    for band in BANDS:
        on, osh, ome = op.get(band, (0, 0.0, 0.0))
        rn, rsh, rme = rp.get(band, (0, 0.0, 0.0))
        if on == 0 and rn == 0:
            continue
        # exact: the change in this band's contribution to the overall mean
        contrib = (osh * ome) - (rsh * rme)
        explained += contrib
        print("  %-14s %-22s %-22s %+.2f B" % (
            "%d..%d" % band, "%d / %5.1f%%" % (on, 100 * osh), "%d / %5.1f%%" % (rn, 100 * rsh), contrib))

    print("  " + "-" * 84)
    print("  %-14s %-45s %+.2f B" % ("total", "sum of contributions", explained))
    print()
    print("  The sum matches the mean difference by construction: each band's share times its own mean size, differenced.")
    print("  A band contributing positively means the original puts more of its mean there, not that it has more code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())