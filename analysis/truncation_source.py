"""Is the truncation in the binary, or only in my string dump? (R668)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); this parses the PE
headers and reads file bytes directly, same route as R631-R651.

**Why**: criterion (b) says the remaining copy gaps are "truncated in the string pool". The two keys in question appear
twice -- complete in one place (`0x03C65058`, `0x03C65099`) and cut short in two others
(`0x03C7575C` ends at `": "`, `0x03C7579B` ends at `"{1}`). Whether that is a property of the **binary** or of my
**dump** decides what (b) even means: a binary truncation is unobtainable data; a dump truncation is my own tool's
limit and is fixable.

So: read the raw bytes at those RVAs and print what actually follows.
"""

import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
TARGETS = [0x03C65058, 0x03C65099, 0x03C7575C, 0x03C7579B, 0x03C974F4]


def sections(path):
    data = open(path, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt = struct.unpack_from("<H", data, pe + 20)[0]
    base = pe + 24 + opt
    out = []
    for i in range(nsec):
        off = base + i * 40
        name = data[off:off + 8].rstrip(b"\x00").decode("ascii", "replace")
        vsize, vaddr, rsize, roff = struct.unpack_from("<IIII", data, off + 8)
        out.append((name, vaddr, max(vsize, rsize), roff))
    return data, out


def rva_to_off(secs, rva):
    for name, vaddr, size, roff in secs:
        if vaddr <= rva < vaddr + size:
            return name, roff + (rva - vaddr)
    return None, None


def main():
    data, secs = sections(EXE)
    print("sections: %s" % ", ".join("%s@0x%X" % (n, v) for n, v, _s, _r in secs))
    print()
    for rva in TARGETS:
        name, off = rva_to_off(secs, rva)
        if off is None:
            print("0x%08X  not mapped" % rva)
            continue
        window = data[off:off + 220]
        print("0x%08X  %s +0x%X" % (rva, name, off))
        print("   raw: %r" % window[:200])
        # how far does the JSON key/value run before a non-printable?
        run = 0
        for b in window:
            if 0x20 <= b < 0x7F or b in (0x09, 0x0A, 0x0D):
                run += 1
            else:
                break
        print("   printable run from this RVA: %d bytes" % run)
        print()


if __name__ == "__main__":
    sys.exit(main())
