"""Resolve the fake-data record frame, and with it answer whether `state` carries a country field. (R672)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); reads PE bytes.

**Why**: R671 rejected two stride hypotheses and left the frame Unknown, but the hex view suggested a third shape that
nobody had tested: `<0x02><decimal index><NUL><u32 LE length><text><NUL>`. If that shape walks the `state` table
exactly, two things follow at once -- the frame is known, and each entry holds **only** (index, text), so the table
does **not** carry a country field, which is precisely the question this round asks.

**Criterion, fixed before measuring** -- H3 is ACCEPTED only if all four hold for the `state` table:
  1. parsing starts right after the table name's trailing NUL and its 4-byte field;
  2. it yields exactly **604** entries;
  3. the indices are exactly 0..603 with no gaps;
  4. every payload is printable ASCII with no leftover bytes between entries.

Any failure rejects H3 and the raw bytes at that point are reported instead of a guessed frame.
"""

import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
TABLE_RVA = 0x037514A5
EXPECTED = 604


def load():
    data = open(EXE, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt = struct.unpack_from("<H", data, pe + 20)[0]
    base = pe + 24 + opt
    for i in range(nsec):
        off = base + i * 40
        vaddr, rsize, roff = struct.unpack_from("<III", data, off + 12)
        if vaddr <= TABLE_RVA < vaddr + rsize:
            return data, roff + (TABLE_RVA - vaddr)
    return data, None


def main():
    data, off = load()
    if off is None:
        print("not mapped")
        return 1

    # skip the table name and its 4-byte field
    name_end = data.find(b"\x00", off)
    pos = name_end + 1 + 4
    print("table name at 0x%X, body starts at 0x%X" % (off, pos))
    print("bytes at body start: %r" % data[pos:pos + 24])
    print()

    entries = []
    bad = None
    while len(entries) < EXPECTED + 4:
        if data[pos] != 0x02:
            bad = ("expected 0x02 marker", pos, data[pos:pos + 16])
            break
        pos += 1
        z = data.find(b"\x00", pos, pos + 6)
        if z < 0:
            bad = ("no NUL after index", pos, data[pos:pos + 16])
            break
        idx_text = data[pos:z]
        if not idx_text.isdigit():
            bad = ("index not decimal", pos, idx_text)
            break
        idx = int(idx_text)
        pos = z + 1
        n = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if n == 0 or n > 80:
            bad = ("implausible length %d" % n, pos, data[pos:pos + 16])
            break
        payload = data[pos:pos + n]
        pos += n
        if not payload.endswith(b"\x00"):
            bad = ("payload not NUL-terminated", pos, payload[:24])
            break
        entries.append((idx, payload[:-1]))

    print("entries parsed: %d" % len(entries))
    if entries:
        print("  first 5: %s" % ", ".join("%d=%r" % (i, t) for i, t in entries[:5]))
        print("  last  3: %s" % ", ".join("%d=%r" % (i, t) for i, t in entries[-3:]))
    if bad:
        print("  STOPPED: %s at 0x%X -> %r" % (bad[0], bad[1], bad[2]))
    print()

    idxs = [i for i, _t in entries]
    ok_count = len(entries) == EXPECTED
    ok_idx = idxs == list(range(EXPECTED))
    ok_ascii = all(all(32 <= b < 127 for b in t) for _i, t in entries)
    print("check 1 (entry count == %d) : %s" % (EXPECTED, ok_count))
    print("check 2 (indices 0..%d)      : %s" % (EXPECTED - 1, ok_idx))
    print("check 3 (payloads printable) : %s" % ok_ascii)
    print()
    verdict = "ACCEPTED" if (ok_count and ok_idx and ok_ascii and not bad) else "REJECTED"
    print("H3 verdict: %s" % verdict)
    if verdict == "ACCEPTED":
        print()
        print("=> each entry is exactly (index, text): the state table carries NO country field.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
