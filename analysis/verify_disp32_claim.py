"""Independently verify the rip-relative disp32 claim from raw PE bytes (R703).

The R702 report says a frozen string object at VA 0x146E4D160 is referenced from code site 0x140F7739E via a
`lea reg, [rip+disp32]`, and that IDA's xref/pointer channels never see it. If true, that corrects R691's conclusion:
"no xref and no pointer" was measured correctly, but it was read as "no reference", which is a stronger statement.

**Criterion, fixed before measuring**: at the code RVA of the claimed site, the four bytes immediately following the
opcode must satisfy `site_va + 4 + int32(disp) == target_va` (allowing a small negative offset if the displacement
points at the object header rather than its first byte). This is arithmetic on file bytes -- no IDA, no report tool.
"""

import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
IMAGEBASE = 0x140000000

# claimed by R702
SITE_VA = 0x140F7739E
TARGET_VA = 0x146E4D160   # `ProfileCsv.Error.UnknownCountry` frozen object
# an independent known instance for a control: TEMP, claimed site 0x140F39DE0 -> object at ...?
CONTROL_SITE = 0x140F39DE0


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


def r2o(secs, rva):
    for _n, v, size, r in secs:
        if v <= rva < v + size:
            return r + (rva - v)
    return None


def probe(data, secs, site_va, label):
    rva = site_va - IMAGEBASE
    off = r2o(secs, rva)
    if off is None:
        print("  %-10s site 0x%X not mapped" % (label, site_va))
        return
    window = data[max(0, off - 6):off + 12]
    print("  %-10s site 0x%X  bytes[:18] = %s" % (label, site_va, window.hex(" ")))
    for delta in range(-2, 3):
        p = off + delta
        if p < 0 or p + 4 > len(data):
            continue
        disp = struct.unpack_from("<i", data, p)[0]
        target = site_va + delta + 4 + disp
        if 0x140000000 <= target < 0x148000000:
            print("       +%+d: disp=%d  ->  0x%X" % (delta, disp, target))


def main():
    data, secs = sections(EXE)
    print("imagebase 0x%X, file %d bytes" % (IMAGEBASE, len(data)))
    print()
    probe(data, secs, SITE_VA, "claimed")
    print()
    probe(data, secs, CONTROL_SITE, "control")
    print()
    print("claim target: 0x%X" % TARGET_VA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
