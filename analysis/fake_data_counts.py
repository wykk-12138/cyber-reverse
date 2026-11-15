"""Count entries per fake-data table, and use the count to test the header field. (R671b)

**Why**: R671's hex view showed the layout has two plausible strides and the length prefix lands differently in
different records, so building a parser on a guessed stride would be inventing a format. But one thing *is* legible
without the stride: right after each table's NUL-terminated name there are 4 bytes, and each entry appears to carry a
decimal index.

**So this tests the header count against the data instead of assuming the stride**: for each table, read the 4 bytes
after its name as a little-endian u32, then count how many distinct `\\x02<decimal>\\x00` index tokens appear before the
next table's name. If the two agree for every table, the header field is the entry count -- **which is a fact about
the data independent of how entries are framed**.

**Validation, fixed before running**: the header field is accepted as "entry count" only if it equals the number of
distinct indices found, for **all three** tables. One table agreeing would be coincidence.
"""

import re
import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
TABLES = [b"country", b"building_number", b"street_suffix", b"state", b"city_prefix"]


def load():
    data = open(EXE, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt = struct.unpack_from("<H", data, pe + 20)[0]
    base = pe + 24 + opt
    for i in range(nsec):
        off = base + i * 40
        vaddr, rsize, roff = struct.unpack_from("<III", data, off + 12)
        if vaddr <= 0x037D5824 < vaddr + rsize:
            return data, roff + (0x037D5824 - vaddr)
    return data, None


def main():
    data, anchor = load()
    if anchor is None:
        print("anchor not mapped")
        return 1

    # every table name in this neighbourhood, with its offset
    found = []
    for name in TABLES:
        pat = name + b"\x00"
        start = max(0, anchor - 0x4000)
        idx = data.find(pat, start, anchor + 0x20000)
        if idx >= 0:
            found.append((idx, name))
    found.sort()
    print("tables found in the region: %s" % ", ".join(n.decode() for _i, n in found))
    print()

    for k, (idx, name) in enumerate(found):
        after = data[idx + len(name) + 1:idx + len(name) + 5]
        header = struct.unpack("<I", after)[0]
        limit = found[k + 1][0] if k + 1 < len(found) else idx + 0x20000
        body = data[idx:limit]
        indices = re.findall(rb"\x02(\d{1,4})\x00", body)
        distinct = sorted({int(x) for x in indices})
        print("%-16s header u32 = %-6d   index tokens = %-5d   distinct = %-5d   max index = %s"
              % (name.decode(), header, len(indices), len(distinct), distinct[-1] if distinct else "-"))
        print("                 contiguous 0..%s : %s" % (distinct[-1] if distinct else "-",
                                                         distinct == list(range(len(distinct)))))
    print()
    print("header field is the entry count only if it equals 'distinct' for every table above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
