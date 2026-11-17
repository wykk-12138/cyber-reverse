"""Print both images' section tables, so the 0x1C00000 boundary can be checked against the layout.

R969 found the replica's .pdata covering 0x0..0x1B00000 and nothing above, while the original runs to 0x3100000. Before
concluding that the replica's code "ends", one thing has to be ruled out: whether 0x1C00000.. in the original is still the
text section or a different section entirely. If it is a different section, the comparison is between unlike things and the
conclusion changes shape.

Writes nothing; reads only the two PE headers.
"""

import io
import os
import struct

ROOT = r"D:\projects\cyber-reverse\replica"
ORIGINAL = os.path.abspath(os.path.join(ROOT, "..", "target", "Cybersole.exe"))
REPLICA = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")


def sections(path):
    if not os.path.exists(path):
        return None, []
    data = io.open(path, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    image_base = struct.unpack_from("<Q" if magic == 0x20B else "<I", data,
                                    opt + (24 if magic == 0x20B else 28))[0]
    table = opt + opt_size
    out = []
    for i in range(count):
        h = table + i * 40
        name = data[h:h + 8].rstrip(b"\x00").decode("ascii", "replace")
        vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", data, h + 8)
        chars = struct.unpack_from("<I", data, h + 36)[0]
        out.append((name, vaddr, vsize, rsize, rptr, chars))
    return image_base, out


totals = {}
for label, path in (("ORIGINAL", ORIGINAL), ("REPLICA", REPLICA)):
    base, secs = sections(path)
    print("=== %s  image base 0x%X  file %d bytes ===" % (label, base or 0, os.path.getsize(path)))
    print("  %-10s %-12s %-12s %-12s %s" % ("name", "rva start", "rva end", "raw size", "flags"))
    print("  " + "-" * 66)
    executable = 0
    for name, vaddr, vsize, rsize, rptr, chars in secs:
        flags = "X" if chars & 0x20000000 else ("R" if chars & 0x40000000 else "-")
        if chars & 0x80000000:
            flags += "W"
        if chars & 0x20000000:
            executable += rsize
        print("  %-10s 0x%-10X 0x%-10X %-12d %s" % (name, vaddr, vaddr + vsize, rsize, flags))
    print()
    # R977: the mass figure criterion (c) needs, under labels no other tool emits. R970 measured this by hand and then
    # wrote the number into three documents; a number nobody can re-run is the kind that drifts.
    print("  section-mass-%s-executable: %d" % (label.lower(), executable))
    totals[label] = executable

if totals.get("ORIGINAL"):
    print("  section-mass-ratio: %.2f%%" % (100.0 * totals["REPLICA"] / totals["ORIGINAL"]))
    print()
    print("  Executable sections summed by raw size. The ratio is a mass comparison and says nothing about what the")
    print("  code does: the replica links a different BCL and Avalonia, so part of the difference is not its own.")
