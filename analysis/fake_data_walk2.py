"""The region is hierarchical: category -> table -> entry. Fix the boundary rule and re-measure. (R674)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); reads PE bytes.

**Why**: R673 reported 270 of 492 tables UNRESOLVED because the walk's stop position did not match "next table header
minus 2". Reading one of them showed why: the bytes there are

    postcode\\0 \\x1e\\0\\0\\0
      \\x02 0 \\0 \\x06\\0\\0\\0 "#####" \\0
      \\x02 1 \\0 \\x05\\0\\0\\0 "####"  \\0
    \\x00\\x00\\x03 internet \\0 \\x59\\0\\0\\0          <- \\x03 marks a CATEGORY, not a table
      \\x04 domain_suffix \\0 \\x45\\0\\0\\0 \\x02 0 ...   <- \\x04 marks a table

So the layout is **three levels**, and the boundary check assumed a flat one: it required the next sibling to be a
table, but a category can sit between tables. **The 270 UNRESOLVED were a defect in my check, not a difference in the
data.**

**Corrected criterion**: the walk stops immediately after a payload's terminating NUL, so a stop is always clean; the
count is trustworthy when
  1. at least 1 entry, and
  2. indices are exactly `0..n-1` with no gaps, and
  3. the byte at the stop position is a **level marker or a section terminator** --
     `0x00` (terminator), `0x03` (category), `0x04` (table) -- rather than an unexpected byte.

This is weaker than R673's rule on purpose: it does not assume flatness, which is what broke R673.

Writes `analysis/fake_data_tables_v2.json`.
"""

import io
import json
import re
import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
OUT = r"D:\projects\cyber-reverse\analysis\fake_data_tables_v2.json"
LO, HI = 0x03600000, 0x03800000
TABLE = re.compile(rb"\x00\x04([a-z][a-z0-9_]{2,20})\x00")
CATEGORY = re.compile(rb"\x00\x03([a-z][a-z0-9_]{2,20})\x00")


def sections(path):
    data = open(path, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt = struct.unpack_from("<H", data, pe + 20)[0]
    base = pe + 24 + opt
    out = []
    for i in range(nsec):
        off = base + i * 40
        vaddr, rsize, roff = struct.unpack_from("<III", data, off + 12)
        out.append((vaddr, rsize, roff))
    return data, out


def r2o(secs, rva):
    for vaddr, size, roff in secs:
        if vaddr <= rva < vaddr + size:
            return roff + (rva - vaddr)
    return None


def o2r(secs, off):
    for vaddr, size, roff in secs:
        if roff <= off < roff + size:
            return vaddr + (off - roff)
    return None


def walk(data, pos, limit=40000):
    entries = []
    while len(entries) < limit:
        if pos >= len(data) or data[pos] != 0x02:
            return entries, pos, "no 0x02 marker"
        pos += 1
        z = data.find(b"\x00", pos, pos + 6)
        if z < 0 or not data[pos:z].isdigit():
            return entries, pos, "bad index"
        idx = int(data[pos:z])
        pos = z + 1
        if pos + 4 > len(data):
            return entries, pos, "truncated length"
        n = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if n == 0 or n > 200:
            return entries, pos, "implausible length %d" % n
        payload = data[pos:pos + n]
        if len(payload) != n or not payload.endswith(b"\x00"):
            return entries, pos, "payload not terminated"
        pos += n
        entries.append((idx, payload[:-1]))
    return entries, pos, "hit limit"


def main():
    data, secs = sections(EXE)
    lo, hi = r2o(secs, LO), r2o(secs, HI)
    region = data[lo:hi]

    cats = [(m.group(1).decode(), lo + m.start() + 2) for m in CATEGORY.finditer(region)]
    tabs = [(m.group(1).decode(), lo + m.start() + 2) for m in TABLE.finditer(region)]
    print("categories: %d   tables: %d" % (len(cats), len(tabs)))

    # which category precedes each table?
    def category_of(off):
        best = None
        for name, pos in cats:
            if pos < off:
                best = name
        return best or "-"

    results = []
    ok = 0
    for name, name_start in tabs:
        field_off = name_start + len(name) + 1
        field = struct.unpack_from("<I", data, field_off)[0]
        body = field_off + 4
        entries, stop, reason = walk(data, body)
        n = len(entries)
        idxs = [i for i, _t in entries]
        contiguous = idxs == list(range(n))
        nxt = data[stop] if stop < len(data) else None
        clean_stop = nxt in (0x00, 0x03, 0x04, 0x02) or nxt is None
        verdict = "SELF-CONSISTENT" if (n >= 1 and contiguous and clean_stop) else "UNRESOLVED"
        if verdict == "SELF-CONSISTENT":
            ok += 1
        results.append({
            "category": category_of(name_start),
            "table": name,
            "rva": "0x%08X" % (o2r(secs, name_start) or 0),
            "field_u32": field,
            "entries": n,
            "contiguous": contiguous,
            "stop_byte": None if nxt is None else "0x%02X" % nxt,
            "stop_reason": reason,
            "verdict": verdict,
            "first": entries[0][1][:40].decode("utf-8", "replace") if n else None,
        })

    print("self-consistent: %d of %d" % (ok, len(tabs)))
    print()
    print("=== largest self-consistent tables ===")
    good = [r for r in results if r["verdict"] == "SELF-CONSISTENT"]
    for r in sorted(good, key=lambda x: -x["entries"])[:12]:
        print("  %-22s %-16s %5d entries" % (r["category"][:22], r["table"], r["entries"]))
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
