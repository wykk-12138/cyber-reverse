"""Dump a hex view with absolute RVAs of the fake-data region, so the record layout can be read off. (R671)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); this parses PE
headers and reads file bytes, same route as R668/R669/R670.

**Why**: R670 found the region and recognised three tables inside it, but the record layout was inferred from a
repr() and the byte alignment was ambiguous -- the prefix looked like `\\x00\\x04` before the first record and absent
before the second. Guessing the layout from a repr is how a parser gets built on a wrong stride, so this prints the
bytes aligned against their addresses and stops there.

Read-only. Prints; writes nothing.
"""

import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
START = 0x037D5800
LENGTH = 0x300


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


def main():
    data, secs = sections(EXE)
    off = rva_to_off(secs, START)
    if off is None:
        print("not mapped")
        return 1
    blob = data[off:off + LENGTH]
    print("RVA 0x%08X -> file offset 0x%X, %d bytes" % (START, off, len(blob)))
    print()
    for i in range(0, len(blob), 16):
        chunk = blob[i:i + 16]
        hexpart = " ".join("%02x" % b for b in chunk)
        text = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in chunk)
        print("0x%08X  %-47s  %s" % (START + i, hexpart, text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
