"""Count the non-leaf functions in both artifacts, from .pdata. (R832)

WHY THIS EXISTS (AGENTS.md §1.2 requires the reason be stated):

The goal's first clause is that the function counts be equal, and until R831 no metric covered it -- METRICS.md's six
entries all count declarations (binding gaps, absent types, member shapes, copy, backlog, descriptor tables) because
counting declarations is cheaper than counting artifacts. R831 measured it with a one-off script, which leaves the
number unreproducible, and a number nobody can re-run is the kind that drifts.

func_compare.py could answer it, but it needs two IDA instances: the original on 13337 and the replica on 13338, and the
second is usually not running. It also compares IDA's `af` count, which requires a full auto-analysis of the replica to
get. The `.pdata` RUNTIME_FUNCTION table is present in both PE images, needs no disassembly, and answers the question in
under a second -- so it is the measure this metric uses.

What it can and cannot say, stated here so the number is not read as more than it is:
    CAN   : compare function mass between the two artifacts on one identical measure.
    CANNOT: establish function-level equality (`.pdata` counts non-leaf functions and excludes inlined and trimmed
            code), nor be compared with IDA's 321,244 `af` count, nor attribute the difference to the replica's own
            code rather than to Avalonia and a different BCL.

Reproduce:
    cd replica
    python tools/func_count.py
"""

import io
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORIGINAL = os.path.abspath(os.path.join(ROOT, "..", "target", "Cybersole.exe"))
REPLICA = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")

RUNTIME_FUNCTION_BYTES = 12  # x64: BeginAddress, EndAddress, UnwindInfoAddress -- three DWORDs


def pdata_functions(path):
    """Return the RUNTIME_FUNCTION count, or None when the section is absent or the file is missing."""
    if not os.path.exists(path):
        return None
    data = open(path, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\x00\x00":
        return None
    sections = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    table = pe + 24 + optional_size
    for i in range(sections):
        head = table + i * 40
        name = data[head:head + 8].rstrip(b"\x00").decode("ascii", "replace")
        if name != ".pdata":
            continue
        _vsize, _vaddr, raw_size, _raw_ptr = struct.unpack_from("<IIII", data, head + 8)
        return raw_size // RUNTIME_FUNCTION_BYTES
    return None


def main():
    original = pdata_functions(ORIGINAL)
    replica = pdata_functions(REPLICA)

    print("function count (non-leaf, from .pdata):")
    print("  pdata-original: %s" % (original if original is None else format(original, ",")))
    print("  pdata-replica: %s" % (replica if replica is None else format(replica, ",")))

    if original is None or replica is None:
        print("  pdata-ratio: n/a -- one artifact is missing or has no .pdata")
        print("  NOTE: metrics_report runs before the AOT publish in some flows; a missing replica artifact is a")
        print("        missing measurement, not a zero, and this line says so rather than printing 0.0")
        return 1

    ratio = replica / original
    print("  pdata-ratio: %.2f%%" % (ratio * 100.0))
    print("  .pdata holds one RUNTIME_FUNCTION per non-leaf function: it excludes inlined and trimmed code, so this")
    print("  compares function mass between the two images and does not establish function-level equality.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
