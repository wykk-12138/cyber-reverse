"""Read a string through an off_ slot, distinguishing the slot from the object it points at. (R806)

D:\projects\cyber-reverse\analysis\off_slot_reader.py reads object+12 and calibrated on off_1471151D0 -> 'poq-app-id',
but that symbol turned out to be a string object rather than a slot: here every 0x146B5E** address returned
'BillingAddressFormView' with a different length each time, which cannot be right for one string and means the
characters were fetched from the wrong place.

So this reads both interpretations and picks the one whose stored length agrees with the number of characters
actually present. If neither agrees it says so rather than guessing.

Why not the existing script: it hard-codes one interpretation and one calibration point. Rather than edit a tool other
rounds rely on, this keeps the two interpretations explicit and self-checking.
"""

import json
import struct
import subprocess
import sys

IDA = r"D:\projects\cyber-reverse\analysis\ida.py"
EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
IMAGE_BASE = 0x140000000


def sections():
    """Section table from the PE headers, so a VA can be turned into a file offset."""
    data = open(EXE, "rb").read(0x2000)
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    opt = e_lfanew + 24
    size_opt = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    out = []
    for i in range(nsec):
        off = opt + size_opt + i * 40
        name = data[off:off + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, off + 8)
        out.append((name, vaddr, vsize, rawptr, rawsize))
    return out


SECS = sections()
BLOB = open(EXE, "rb").read()


def read_va(va, n):
    rva = va - IMAGE_BASE
    for name, vaddr, vsize, rawptr, rawsize in SECS:
        if vaddr <= rva < vaddr + max(vsize, rawsize):
            fo = rawptr + (rva - vaddr)
            return BLOB[fo:fo + n]
    return b""


def as_string(obj_va):
    """+0 method table pointer, +8 DWORD length, +12 UTF-16 characters."""
    head = read_va(obj_va + 8, 4)
    if len(head) < 4:
        return None
    n = struct.unpack("<I", head)[0]
    if not (0 < n < 4096):
        return None
    raw = read_va(obj_va + 12, n * 2)
    if len(raw) < n * 2:
        return None
    try:
        return raw.decode("utf-16-le")
    except Exception:
        return None


def deref(slot_va):
    raw = read_va(slot_va, 8)
    if len(raw) < 8:
        return None
    return struct.unpack("<Q", raw)[0]


def resolve(slot_va):
    """Try the slot as an object, then as a pointer to one; accept only a length-consistent read."""
    direct = as_string(slot_va)
    if direct is not None and len(direct) > 0:
        return direct, "object"

    ptr = deref(slot_va)
    if ptr and IMAGE_BASE <= ptr < IMAGE_BASE + 0x9000000:
        indirect = as_string(ptr)
        if indirect is not None:
            return indirect, "slot->object"
    return None, "unreadable"


slots = [0x146B5E268, 0x146B5E190, 0x146B5E2D0, 0x146B5E1F8, 0x146B5E7C8, 0x146B5E408,
         0x146B5E520, 0x146B5DFB0, 0x146B5E588, 0x146B5E070, 0x146B5E460, 0x146B5E4B8,
         0x146B5E340, 0x146B5E3A0, 0x146B5E138, 0x146AB0028]

for s in slots:
    val, how = resolve(s)
    print("  %-12s %-13s %r" % (hex(s), how, (val or "")[:64]))
