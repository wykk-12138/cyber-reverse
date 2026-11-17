"""Where does the function-count gap actually sit? A distribution, not a total. (R969)

WHY THIS EXISTS (AGENTS.md §1.2 requires the reason be stated):

R968 established that the body-string check can only be read in one direction -- a retained method keeps some of its
literals and drops others, so absence proves nothing -- and left one question standing: the replica is at 173,952
non-leaf functions against the original's 277,120, and nobody knows where the missing 103,168 are. R966 guessed that the
reflection dispatch table was empty in the artifact; R967 disproved that by finding all 179 step names as UTF-8. So the
gap needs a shape rather than another candidate cause.

func_count.py answers "how many" and stops there. This tool answers "where", by bucketing every RUNTIME_FUNCTION by its
BeginAddress and comparing the two histograms. It reuses func_count's PE parsing rather than writing a second parser,
because two parsers that disagree is one more thing to debug than one.

What it can and cannot say:
    CAN   : show whether the gap is concentrated in a few address ranges or spread across all of them.
    CANNOT: name what lives in a range. The two images are laid out independently, so matching buckets across them is a
            comparison of density, not of identity -- a bucket with equal counts is not the same code. It also cannot
            distinguish "not written" from "written and trimmed", which needs the names, not the addresses.

Reproduce:
    cd replica
    python tools/pdata_sections.py                 # 1 MiB buckets
    python tools/pdata_sections.py --bucket 0x40000
"""

import argparse
import collections
import io
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORIGINAL = os.path.abspath(os.path.join(ROOT, "..", "target", "Cybersole.exe"))
REPLICA = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")

RUNTIME_FUNCTION_BYTES = 12  # x64: BeginAddress, EndAddress, UnwindInfoAddress


def pdata_extents(path):
    """Return [(begin, end)] from .pdata, or [] when absent. Same section walk, extents kept.

    R971. An entry whose end is not above its begin, or is more than a mebibyte above it, is not a function extent and is
    dropped rather than counted as a one-byte or a two-megabyte function.
    """
    if not os.path.exists(path):
        return []

    data = open(path, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\x00\x00":
        return []

    sections = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    table = pe + 24 + optional_size

    for i in range(sections):
        head = table + i * 40
        name = data[head:head + 8].rstrip(b"\x00").decode("ascii", "replace")
        if name != ".pdata":
            continue
        _vsize, _vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", data, head + 8)
        out = []
        for off in range(0, raw_size - RUNTIME_FUNCTION_BYTES + 1, RUNTIME_FUNCTION_BYTES):
            begin, end, _unwind = struct.unpack_from("<III", data, raw_ptr + off)
            if 0 < end - begin < 0x100000:
                out.append((begin, end))
        return out

    return []


def report_sizes(label, path):
    entries = pdata_extents(path)
    sizes = sorted(e - b for b, e in entries)
    if not sizes:
        print("  %-9s no .pdata or no extents" % label)
        return
    n = len(sizes)
    total = sum(sizes)
    print("  %-9s funcs=%-7d total=%d B  mean=%.1f  median=%-5d p90=%-5d p99=%-6d max=%d" % (
        label, n, total, total / n, sizes[n // 2], sizes[int(n * 0.9)], sizes[int(n * 0.99)], sizes[-1]))
    small = sum(1 for x in sizes if x <= 64)
    mid = sum(1 for x in sizes if 64 < x <= 512)
    big = sum(1 for x in sizes if x > 512)
    print("             <=64B: %-6d (%4.1f%%)   65..512B: %-6d (%4.1f%%)   >512B: %-5d (%4.1f%%)" % (
        small, 100.0 * small / n, mid, 100.0 * mid / n, big, 100.0 * big / n))


def pdata_begins(path):
    """Return (image_base, [BeginAddress...]) or (None, []) when the section or file is missing.

    Same section walk as func_count.pdata_functions, extended to keep the addresses. Returning the image base matters
    because the two artifacts are based differently; without it the buckets would not be comparable at all.
    """
    if not os.path.exists(path):
        return None, []

    data = open(path, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\x00\x00":
        return None, []

    sections = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    optional = pe + 24

    magic = struct.unpack_from("<H", data, optional)[0]
    image_base = struct.unpack_from("<Q" if magic == 0x20B else "<I", data,
                                    optional + (24 if magic == 0x20B else 28))[0]

    table = optional + optional_size
    for i in range(sections):
        head = table + i * 40
        name = data[head:head + 8].rstrip(b"\x00").decode("ascii", "replace")
        if name != ".pdata":
            continue
        _vsize, _vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", data, head + 8)
        begins = []
        for off in range(0, raw_size - RUNTIME_FUNCTION_BYTES + 1, RUNTIME_FUNCTION_BYTES):
            begin = struct.unpack_from("<I", data, raw_ptr + off)[0]
            begins.append(begin)
        return image_base, begins

    return None, []


def histogram(begins, bucket):
    counts = collections.Counter()
    for b in begins:
        counts[b // bucket] += 1
    return counts


def main():
    ap = argparse.ArgumentParser(description="Compare the two .pdata tables as address-bucket histograms.")
    ap.add_argument("--bucket", default="0x100000", help="bucket size in bytes, hex or decimal (default 1 MiB)")
    ap.add_argument("--sizes", action="store_true",
                    help="report the function size distribution instead of address buckets (R971)")
    args = ap.parse_args()

    if args.sizes:
        print("pdata function size distribution (bytes per non-leaf function)")
        print("  entries whose extent is zero or over 1 MiB are excluded as not being function extents")
        print()
        report_sizes("ORIGINAL", ORIGINAL)
        report_sizes("REPLICA", REPLICA)
        print()
        print("  A size difference is not a behaviour difference: a function twice as long is not two functions' worth.")
        return 0

    bucket = int(args.bucket, 0)

    o_base, o_begins = pdata_begins(ORIGINAL)
    r_base, r_begins = pdata_begins(REPLICA)

    print("pdata bucket histogram (bucket = 0x%X bytes)" % bucket)
    print("  original: %s functions, image base 0x%X" % (format(len(o_begins), ","), o_base or 0))
    print("  replica : %s functions, image base 0x%X" % (format(len(r_begins), ","), r_base or 0))

    if not o_begins or not r_begins:
        print("  one artifact is missing or has no .pdata -- this is a missing measurement, not a zero")
        return 1

    oh = histogram(o_begins, bucket)
    rh = histogram(r_begins, bucket)
    keys = sorted(set(oh) | set(rh))

    print()
    print("  %-14s %-10s %-10s %s" % ("range from", "original", "replica", "replica/original"))
    print("  " + "-" * 52)

    worst = []
    for k in keys:
        o, r = oh.get(k, 0), rh.get(k, 0)
        pct = "%6.1f%%" % (100.0 * r / o) if o else "     --"
        print("  0x%-12X %-10s %-10s %s" % (k * bucket, format(o, ","), format(r, ","), pct))
        if o >= 500:
            worst.append((100.0 * r / o, k, o, r))

    print()
    worst.sort()
    print("  the five thinnest buckets with at least 500 original functions:")
    for pct, k, o, r in worst[:5]:
        print("    0x%-12X %5.1f%%   original %-8s replica %s" % (k * bucket, pct, format(o, ","), format(r, ",")))

    # R977: criterion (c) should read these from one place. R969 measured the boundary by eye and then wrote it into three
    # documents; these three labels make it a number another run can reproduce.
    #
    # The keys of oh/rh are bucket INDICES, not addresses -- the first cut of this compared an index against 0x1C00000 and
    # dutifully reported zero in both images. Compare in address space, which is what the boundary is stated in.
    boundary = 0x1C00000
    above_o = sum(v for k, v in oh.items() if k * bucket >= boundary)
    above_r = sum(v for k, v in rh.items() if k * bucket >= boundary)
    print()
    print("  pdata-above-0x1C00000-original: %d" % above_o)
    print("  pdata-above-0x1C00000-replica: %d" % above_r)
    print("  pdata-last-replica-bucket: 0x%X" % (max(rh) * bucket))

    print()
    print("  Buckets are compared by density, not by identity: the two images are laid out independently, so equal")
    print("  counts in a bucket do not mean the same code. This says where the gap sits and nothing about why.")
    return 0


if __name__ == "__main__":
    sys.exit(main())