"""Walk every fake-data table by the validated record frame, and let the walk define each table's boundary. (R673)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); reads PE bytes.

**Why**: R672 validated the record frame `<0x02><index><NUL><u32 LE len><payload><NUL>` by having it terminate exactly
at the next table header, and showed the earlier entry counts were wrong because they counted inside an unbounded
window. So the boundary is not something to search for -- **the walk produces it**: parse until the frame stops
matching, and where it stops is the end of the table.

**Criterion, fixed before measuring**: a table is **SELF-CONSISTENT** when
  1. the walk yields at least 1 entry,
  2. indices are exactly `0..n-1` with no gaps,
  3. the walk's stop position is **the next header's name position minus 2** (the `\\x00\\x04` marker),
     i.e. the walk consumes the table exactly, with no slack and no overshoot.

A table whose walk satisfies all three has a trustworthy count. A table whose walk fails is reported as
**UNRESOLVED** with the byte it stopped on -- not given a number.

Writes `analysis/fake_data_tables.json`.
"""

import io
import json
import re
import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
OUT = r"D:\projects\cyber-reverse\analysis\fake_data_tables.json"
LO, HI = 0x03600000, 0x03800000
HEADER = re.compile(rb"\x00\x04([a-z][a-z0-9_]{2,20})\x00")


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


def rva_to_off(secs, rva):
    for vaddr, size, roff in secs:
        if vaddr <= rva < vaddr + size:
            return roff + (rva - vaddr)
    return None


def off_to_rva(secs, off):
    for vaddr, size, roff in secs:
        if roff <= off < roff + size:
            return vaddr + (off - roff)
    return None


def walk(data, pos, limit=20000):
    """Parse entries under the R672 frame. Returns (entries, stop_pos, reason)."""
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
    lo_off = rva_to_off(secs, LO)
    hi_off = rva_to_off(secs, HI)
    region = data[lo_off:hi_off]

    headers = []
    for m in HEADER.finditer(region):
        name = m.group(1).decode()
        name_start = lo_off + m.start() + 2
        field_off = name_start + len(m.group(1)) + 1
        field = struct.unpack_from("<I", data, field_off)[0]
        body = field_off + 4
        headers.append((name, name_start, field, body))

    print("headers found: %d in RVA 0x%X..0x%X" % (len(headers), LO, HI))
    print()

    results = []
    ok = 0
    for k, (name, name_start, field, body) in enumerate(headers):
        entries, stop, reason = walk(data, body)
        n = len(entries)
        idxs = [i for i, _t in entries]
        contiguous = idxs == list(range(n))

        # the walk must stop exactly where the next header's 0x00 0x04 marker begins
        exact = False
        if k + 1 < len(headers):
            next_marker = headers[k + 1][1] - 2
            exact = stop == next_marker
        else:
            exact = reason != "no 0x02 marker"

        verdict = "SELF-CONSISTENT" if (n >= 1 and contiguous and exact) else "UNRESOLVED"
        if verdict == "SELF-CONSISTENT":
            ok += 1
        rva = off_to_rva(secs, name_start)
        results.append({
            "table": name,
            "rva": "0x%08X" % (rva or 0),
            "field_u32": field,
            "entries": n,
            "contiguous": contiguous,
            "stop_exact": exact,
            "stop_reason": reason,
            "verdict": verdict,
            "first": entries[0][1][:40].decode("utf-8", "replace") if n else None,
        })
        if n >= 1 and contiguous:
            mark = "ok " if verdict == "SELF-CONSISTENT" else "!! "
            print("%s%-16s @0x%08X  field=%-7d entries=%-5d %s" %
                  (mark, name, rva or 0, field, n,
                   "" if exact else "(stop: %s)" % reason))

    print()
    print("self-consistent: %d of %d" % (ok, len(headers)))
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
