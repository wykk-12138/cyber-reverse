"""Extract UTF-16LE strings from a PE without IDA.

**Known blind spot (R668/R669)**: both extractors below accept ASCII only -- `utf16_runs` requires the
high byte to be 0, and `utf8_runs` matches `[\x20-\x7e]`. Every Japanese / Chinese / Korean locale blob
is therefore cut into ASCII fragments, and this file contains **zero** non-ASCII bytes.
Use `pe_strings_utf8.py` when multi-byte text matters; it recovers 4,579 CJK strings this one loses.

R94: the IDA database is gone (R93's crash + Repair), so the reverse-engineering half of the loop
has no tool. A NativeAOT image keeps its string literals as UTF-16LE runs in the data section, and
those are readable with nothing but the file — which is exactly what the platform map needs.

Usage:
    python pe_strings.py <exe> <out.txt> [min_len]
"""
import io
import re
import sys


def utf16_runs(data: bytes, min_len: int = 6):
    """Yield (offset, text) for every run of printable UTF-16LE characters."""
    # Walk the buffer as UTF-16LE and cut at the first non-printable code unit.
    i = 0
    n = len(data)
    start = None
    chars = []

    while i + 1 < n:
        lo, hi = data[i], data[i + 1]
        # printable ASCII or latin-1 in the low byte, NUL high byte
        if hi == 0 and (0x20 <= lo <= 0x7E or lo in (0x09,)):
            if start is None:
                start = i
            chars.append(chr(lo))
        else:
            if start is not None and len(chars) >= min_len:
                yield start, "".join(chars)
            start = None
            chars = []
        i += 2

    if start is not None and len(chars) >= min_len:
        yield start, "".join(chars)


def utf8_runs(data: bytes, min_len: int = 6):
    """Yield printable ASCII runs too — NativeAOT keeps some literals as narrow strings."""
    pattern = re.compile(rb"[\x20-\x7e]{%d,}" % min_len)
    for m in pattern.finditer(data):
        yield m.start(), m.group().decode("ascii", "replace")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    path, out_path = sys.argv[1], sys.argv[2]
    min_len = int(sys.argv[3]) if len(sys.argv) > 3 else 6

    data = io.open(path, "rb").read()
    print("read %d bytes from %s" % (len(data), path))

    seen = set()
    lines = []
    for offset, text in list(utf16_runs(data, min_len)) + list(utf8_runs(data, min_len)):
        if text in seen:
            continue
        seen.add(text)
        lines.append("0x%08x  %s" % (offset, text))

    print("distinct strings: %d" % len(lines))
    io.open(out_path, "w", encoding="utf-8", newline="").write("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
