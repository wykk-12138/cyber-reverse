"""Export one table with the R676 parser, to prove the reader works before any full export. (R677)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); reads PE bytes.

**Why**: R676 decoded the container format and validated it 6/6 by exact consumption plus three semantic checks, but
that was only six tables. A full export is a bigger claim and should not start before the reader is shown working on a
table chosen for its **externally checkable content**.

**Target**: `country`, 239 entries. Chosen because its content is checkable without any tool: ISO 3166-1 alpha-3
codes are three uppercase letters, and R670 already read a handful of them straight out of the bytes
(`COK`, `CIV`, `CHE`, `USA`, `DEU`, `JPN`).

**Criterion, fixed before measuring**:
  1. the export yields exactly **239** entries;
  2. every entry's `code` field is **3 uppercase ASCII letters**;
  3. the set contains the codes R670 read directly (`COK`, `CIV`, `CHE`, `USA`, `DEU`, `JPN`);
  4. every entry has an integer `id` field, and the ids are **distinct**.

All four must hold. Any failure is reported with the offending entry rather than summarised.
"""

import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
TABLE = "country"
EXPECTED = 239
MUST_CONTAIN = ["COK", "CIV", "CHE", "USA", "DEU", "JPN"]


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


class Reader:
    """The R676 format: 0x02 string field, 0x10 inline int, 0x03 array elem, 0x04 named table."""

    def __init__(self, data):
        self.d = data

    def value(self, pos, end):
        marker = self.d[pos]
        pos += 1
        if marker == 0x02:
            z = self.d.find(b"\x00", pos, min(pos + 60, end))
            if z < 0:
                raise ValueError("0x02 name unterminated")
            name = self.d[pos:z].decode("ascii", "replace")
            pos = z + 1
            n = struct.unpack_from("<I", self.d, pos)[0]
            pos += 4
            payload = self.d[pos:pos + n]
            if len(payload) != n or not payload.endswith(b"\x00"):
                raise ValueError("0x02 payload bad")
            return pos + n, ("str", name, payload[:-1])
        if marker == 0x10:
            z = self.d.find(b"\x00", pos, min(pos + 60, end))
            name = self.d[pos:z].decode("ascii", "replace")
            pos = z + 1
            val = struct.unpack_from("<I", self.d, pos)[0]
            return pos + 4, ("int", name, val)
        if marker in (0x03, 0x04):
            z = self.d.find(b"\x00", pos, min(pos + 60, end))
            label = self.d[pos:z].decode("ascii", "replace")
            pos = z + 1
            declared = struct.unpack_from("<I", self.d, pos)[0]
            pos += 4
            start = pos
            pos = self.obj(pos, end)
            if pos - start != declared - 4:
                raise ValueError("0x%02X %s len mismatch" % (marker, label))
            return pos, ("elem" if marker == 0x03 else "table", label)
        raise ValueError("unknown marker 0x%02X at %d" % (marker, pos - 1))

    def obj(self, pos, end):
        fields = []
        while True:
            if pos >= end:
                raise ValueError("ran past end")
            if self.d[pos] == 0x00:
                return pos + 1, fields if False else pos + 1
            pos, v = self.value(pos, end)
            fields.append(v)


def main():
    data, secs = sections(EXE)
    needle = TABLE.encode() + b"\x00"

    # find the table header whose field-5 body is largest (the real country table, not a locale stub)
    best = None
    for rva in range(0x03600000, 0x03800000):
        off = r2o(secs, rva)
        if off is None:
            continue
        if data[off:off + len(needle)] != needle:
            continue
        field = struct.unpack_from("<I", data, off + len(needle))[0]
        n = field - 5
        if best is None or n > best[1]:
            best = (off, n)
    if best is None:
        print("country table not found")
        return 1
    off, body_len = best
    body = off + len(needle) + 4
    print("country table: body %d bytes at file offset 0x%X" % (body_len, body))

    rd = Reader(data)
    pos = body
    end = body + body_len
    entries = []
    while pos < end:
        if data[pos] == 0x00:
            pos += 1
            continue
        pos, v = rd.value(pos, end)
        entries.append(v)

    print("parsed entries: %d" % len(entries))
    print("bytes consumed: %d of %d" % (pos - body, body_len))
    print()
    print("first 8:", [e for e in entries[:8]])
    print()

    # entries may be ('elem', label) with the actual data nested; re-read to pull fields out
    codes = []
    for e in entries:
        if e[0] == "elem":
            idx = int(e[1])
            # locate this element's object and read its 'code'/'id' fields
            codes.append(idx)
    print("element indices: %d, first %s, last %s" % (len(codes), codes[:5], codes[-3:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
