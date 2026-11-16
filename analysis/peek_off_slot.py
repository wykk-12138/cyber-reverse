"""Look at the raw bytes around a known off_ slot. (R777 diagnostic)

Written as a file rather than an inline command because the shell has been mangling quoting all session, which is the
same rule AGENTS.md already carries about not writing code through heredocs.
"""

import struct

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
IB = 0x140000000
SECS = [
    (".text", 0x1000, 0x314CE00, 0x400, 0x314CE00),
    (".rdata", 0x314E000, 0x38F8A00, 0x314D200, 0x38F8A00),
    (".data", 0x6A47000, 0x9C1000, 0x6A45C00, 0x9C1000),
]


def foff(va):
    rva = va - IB
    for _n, va0, vs, rp, rs in SECS:
        if va0 <= rva < va0 + max(vs, rs):
            d = rva - va0
            return rp + d if d < rs else None
    return None


data = open(EXE, "rb").read()

for label, va in (("slot  0x1471151d0", 0x1471151D0), ("chars 0x1471151dc", 0x1471151DC)):
    off = foff(va)
    print("  %-18s file=0x%x" % (label, off))
    if off is None:
        print("    not file-backed")
        continue
    print("    hex  : " + data[off:off + 24].hex())
    print("    utf16: %r" % data[off:off + 48].decode("utf-16-le", "replace").split("\x00")[0][:32])
    q = struct.unpack_from("<Q", data, off)[0]
    print("    qword: 0x%x" % q)
    print()

needle16 = "poq-app-id".encode("utf-16-le")
needle8 = b"poq-app-id"
for label, needle in (("utf16", needle16), ("ascii", needle8)):
    j = data.find(needle)
    print("  %s needle at file 0x%x" % (label, j))
    if j > 0:
        # convert back to a VA inside .data when possible
        for _n, va0, vs, rp, rs in SECS:
            if rp <= j < rp + rs:
                print("    -> VA 0x%x" % (IB + va0 + (j - rp)))
