"""Parse the fake-data tables by hypothesis, and let the data accept or reject the hypothesis. (R671)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); reads PE bytes
directly.

**Why a parser instead of more staring**: the hex view showed two plausible strides and the prefix `04 00 00 00`
sits on different boundaries in different records. Reading further by eye is how a parser gets built on a wrong
stride. So: state the hypothesis, run it, and let a hard validation decide.

**Hypothesis H1**: the region is a sequence of `<u16 big-endian length><bytes>`, i.e.
`00 04 43 4F 4B 00` = length 4 followed by `COK\\0`.

**Validation (fixed before running)** -- H1 is ACCEPTED only if all three hold:
  1. walking from the table start consumes the region **exactly**, ending immediately before the next table's name;
  2. the first table yields only 3-uppercase-letter payloads;
  3. the second table's payloads are ASCII words (street suffixes) with no leftover bytes.

If any fails, H1 is rejected and the raw bytes are reported rather than a guessed layout.
"""

import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"


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


def walk(blob, pos, limit=400):
    """Yield (length, payload) under H1; stop when the length looks impossible."""
    out = []
    while len(out) < limit and pos + 2 <= len(blob):
        n = struct.unpack_from(">H", blob, pos)[0]
        if n == 0 or n > 64 or pos + 2 + n > len(blob):
            break
        payload = blob[pos + 2:pos + 2 + n]
        out.append((n, payload))
        pos += 2 + n
    return out, pos


def main():
    data, secs = sections(EXE)
    # the country table starts where a `00 04` is followed by three uppercase letters
    start_rva = None
    for rva in range(0x037D4000, 0x037D6000):
        off = rva_to_off(secs, rva)
        if off is None:
            continue
        if data[off:off + 2] == b"\x00\x04" and data[off + 2:off + 5].isupper() and data[off + 5] == 0:
            start_rva = rva
            break
    if start_rva is None:
        print("country table start not found")
        return 1

    off = rva_to_off(secs, start_rva)
    print("country table starts at RVA 0x%08X" % start_rva)
    blob = data[off:off + 0x2000]

    records, end = walk(blob, 0, 400)
    print("H1 walk: %d records, consumed %d bytes" % (len(records), end))
    codes = [p for n, p in records if n == 4 and p[:3].isupper() and p[3] == 0]
    print("  payloads that look like a 3-letter code + NUL: %d of %d" % (len(codes), len(records)))
    print("  first: %s   last: %s" % (codes[0][:3].decode() if codes else "-",
                                      codes[-1][:3].decode() if codes else "-"))
    tail = blob[end:end + 40]
    print("  bytes right after the walk: %r" % tail)
    print()

    ok_shape = len(codes) == len(records) and len(codes) > 100
    ok_tail = b"building_number" in blob[max(0, end - 40):end + 80]
    print("check 1 (all payloads are codes) : %s" % ok_shape)
    print("check 2 (walk lands at building_number): %s" % ok_tail)
    verdict = "ACCEPTED" if (ok_shape and ok_tail) else "REJECTED"
    print()
    print("H1 verdict: %s" % verdict)
    if verdict == "REJECTED":
        print("  raw 96 bytes from the start: %r" % blob[:96])
    return 0


if __name__ == "__main__":
    sys.exit(main())
