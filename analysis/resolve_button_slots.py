"""Resolve the four `off_` globals that sub_140594500 selects between, to their strings. (R731)

The decompilation shows four branches picking `off_146EB8538`, `off_146EB8588`, `off_146EB85E8` and
`off_146EB8638`, and the catalogue holds four matching labels. Matching them by English sense would be an
inference; reading the pointer out of the image makes it an observation, and this is the crux the implementation
depends on.

**Why not an existing tool** (AGENTS.md §1.2): `read_bytes` through the plugin returned an empty object for these
addresses, and `xrefs_to` answers about code references rather than about what a data slot points at. The PE reader in
`pdata_unwind.py` is already here, so this is a few lines on top of it rather than a new capability.
"""

import io
import os
import struct
import sys

sys.path.insert(0, os.path.join(r"D:\projects\cyber-reverse", "analysis"))
import pdata_unwind as P

A = r"D:\projects\cyber-reverse\target\Cybersole.exe"
SLOTS = ["0x146EB8538", "0x146EB8588", "0x146EB85E8", "0x146EB8638"]
BASE = 0x140000000


def read_string(data, sections, va):
    """Follow a frozen-string object: [MethodTable:8][length:4][chars] with chars at +12."""
    off = P.rva_to_off(sections, va - BASE)
    if off is None:
        return None
    # the slot holds a pointer to the object
    ptr = struct.unpack_from("<Q", data, off)[0]
    if not (BASE <= ptr < BASE + len(data)):
        return "<slot holds 0x%x, not an image pointer>" % ptr
    off2 = P.rva_to_off(sections, ptr - BASE)
    if off2 is None:
        return "<object at 0x%x is outside the file>" % ptr
    length = struct.unpack_from("<I", data, off2 + 8)[0]
    if length > 400:
        return "<length %d looks wrong>" % length
    raw = data[off2 + 12:off2 + 12 + 2 * length]
    try:
        return raw.decode("utf-16-le", "replace")
    except Exception:
        return "<undecodable>"


def main():
    data = open(A, "rb").read()
    _b, _d, sections = P.parse_pe(data)
    for slot in SLOTS:
        print("  %-14s -> %r" % (slot, read_string(data, sections, int(slot, 16))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
