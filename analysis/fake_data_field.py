"""Test `field_u32 == body_byte_length + 5` across every walked table. (R675)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); reads PE bytes.

**Why**: three rounds have now failed to pin the 4-byte field after each table name --
  * R671 rejected "it is the entry count" (0 of 5 tables agreed);
  * R672 tested "it is the body byte length" and rejected it, because four tables were off by exactly +5 and two were
    negative;
  * R675 found the 76 zero-entry tables carry `field == 5` with **no body at all**.

That last observation explains the +5: the field counts **1 NUL + 4 field bytes + body**. R672's negatives were not
evidence against the rule -- they were R672's own next-header detection failing. So this tests the corrected rule.

**Criterion, fixed before measuring**: `field == (stop - body_start) + 5` for a table, where `body_start` is the byte
after the field and `stop` is where the walk stopped. ACCEPTED if it holds for **every** walked table that has at
least one entry; a single mismatch rejects it and the mismatches are listed.
"""

import io
import json
import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
SRC = r"D:\projects\cyber-reverse\analysis\fake_data_tables_v2.json"


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


def walk(data, pos, limit=40000):
    start = pos
    n_entries = 0
    while n_entries < limit:
        if pos >= len(data) or data[pos] != 0x02:
            break
        pos += 1
        z = data.find(b"\x00", pos, pos + 6)
        if z < 0 or not data[pos:z].isdigit():
            break
        pos = z + 1
        if pos + 4 > len(data):
            break
        n = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if n == 0 or n > 200:
            break
        payload = data[pos:pos + n]
        if len(payload) != n or not payload.endswith(b"\x00"):
            break
        pos += n
        n_entries += 1
    return n_entries, pos - start


def main():
    data, secs = sections(EXE)
    rows = json.load(io.open(SRC, encoding="utf-8"))
    ok = bad = empty = 0
    mismatches = []
    for r in rows:
        rva = int(r["rva"], 16)
        off = r2o(secs, rva)
        if off is None:
            continue
        name = r["table"]
        field_off = off + len(name) + 1
        field = struct.unpack_from("<I", data, field_off)[0]
        body = field_off + 4
        entries, body_len = walk(data, body)
        if entries == 0:
            empty += 1
        if field == body_len + 5:
            ok += 1
        else:
            bad += 1
            if len(mismatches) < 10:
                mismatches.append((name, field, body_len, field - body_len))

    print("tables checked      : %d" % (ok + bad))
    print("  field == body + 5 : %d" % ok)
    print("  mismatch          : %d" % bad)
    print("  zero-entry tables : %d" % empty)
    print()
    if mismatches:
        print("=== first mismatches (name, field, body_len, field-body) ===")
        for m in mismatches:
            print("  %-22s %-7d %-7d %d" % m)
    verdict = "ACCEPTED" if bad == 0 else "REJECTED"
    print()
    print("rule `field = body + 5`: %s" % verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
