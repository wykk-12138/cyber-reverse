"""Find the 3-letter-code table by content, not by name. (R678)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); reads PE bytes.

**Why**: R677 set a criterion on `country` and it failed, for two reasons that both had nothing to do with the reader --
the table stores country *names*, and the number 239 belonged to one language instance. The 3-letter codes do exist
(R670 read `index 145 -> COK` straight out of the bytes) but under some other table name. So the name is not a usable
key; the **content** is.

**Criterion, fixed before measuring** -- a table qualifies when
  1. it has **≥ 200** entries, and
  2. **≥ 90 %** of its entry values are exactly **3 uppercase ASCII letters** (`A-Z` only, length 3).

Anything else is reported with its ratio so the threshold is auditable, and the threshold is not moved afterwards.
"""

import re
import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
LO, HI = 0x03600000, 0x03800000
HEADER = re.compile(rb"\x00\x04([a-z][a-z0-9_]{2,20})\x00")
CODE = re.compile(rb"^[A-Z]{3}$")


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


def flat_values(data, body, body_len):
    """Entries of a flat table: 0x02 <idx> NUL <u32 n> <n bytes NUL-terminated>."""
    pos = body
    end = body + body_len
    out = []
    while pos < end:
        if data[pos] != 0x02:
            return None
        pos += 1
        z = data.find(b"\x00", pos, min(pos + 8, end))
        if z < 0 or not data[pos:z].isdigit():
            return None
        pos = z + 1
        if pos + 4 > end:
            return None
        n = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if n == 0 or pos + n > end:
            return None
        payload = data[pos:pos + n]
        if not payload.endswith(b"\x00"):
            return None
        pos += n
        out.append(payload[:-1])
    return out


def main():
    data, secs = sections(EXE)
    lo, hi = r2o(secs, LO), r2o(secs, HI)
    region = data[lo:hi]

    seen = set()
    rows = []
    for m in HEADER.finditer(region):
        name = m.group(1).decode()
        name_off = lo + m.start() + 2
        field_off = name_off + len(m.group(1)) + 1
        field = struct.unpack_from("<I", data, field_off)[0]
        body_len = field - 5
        if body_len <= 0:          # R677: field < 5 means this was a FIELD NAME, not a table header
            continue
        body = field_off + 4
        key = (name, name_off)
        if key in seen:
            continue
        seen.add(key)
        values = flat_values(data, body, body_len)
        if values is None or len(values) < 50:
            continue
        code_like = sum(1 for v in values if CODE.match(v))
        ratio = code_like / len(values)
        rows.append((name, o2r(secs, name_off), len(values), code_like, ratio, values[:4]))

    rows.sort(key=lambda r: -r[4])
    print("tables with >=50 flat entries: %d" % len(rows))
    print()
    print("=== ranked by 3-uppercase-letter ratio ===")
    for name, rva, n, c, ratio, sample in rows[:14]:
        print("  %-20s @0x%08X  n=%-5d codes=%-5d %.0f%%  %s"
              % (name, rva or 0, n, c, 100 * ratio, [s.decode("ascii", "replace") for s in sample]))
    print()

    qualified = [r for r in rows if r[2] >= 200 and r[4] >= 0.90]
    print("meeting the criterion (n>=200 and >=90%% codes): %d" % len(qualified))
    for name, rva, n, c, ratio, _sample in qualified:
        print("  %-20s @0x%08X  n=%d  codes=%d  %.1f%%" % (name, rva or 0, n, c, 100 * ratio))
    return 0


if __name__ == "__main__":
    sys.exit(main())
