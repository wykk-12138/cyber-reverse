"""Resolve the strings behind Hex-Rays `off_XXXX` slots. (R777)

R776 spent three attempts failing to read six header names out of one request builder, and recorded the reason: an
`off_` symbol is the address of a static slot, not a string object, so reading twelve bytes past it returns whatever
the slot holds shifted by twelve. This session has now hit the `off_` family three times -- R715/R731 with four
`off_14492xxxx` slots that all returned the same implausible length, and again last round -- without turning any of it
into a reusable reader. This is that reader.

The layout being probed, from R720 and the -12 rule: a NativeAOT frozen string is an object header followed by UTF-16
characters, and code `lea`s the header, so characters sit twelve bytes in. What an `off_` slot holds is the open
question, and there are three plausible answers:

    1. the object pointer directly (VA, or RVA needing the image base)
    2. a pointer to a descriptor whose first qword is the object pointer
    3. a length-prefixed structure

Rather than assume, this calibrates on a slot whose answer is already known -- `off_1471151D0` holds `poq-app-id`,
because the string at 0x1471151dc is exactly twelve bytes past that slot -- and reports which interpretation
reproduces it. Only then does it apply the same rule to the slots nobody has read.

Usage:
    python analysis/off_slot_reader.py                 # calibrate, then read the Poq request builder's slots
    python analysis/off_slot_reader.py 0x1471151D0 ... # read specific slots

**Why not an existing tool** (AGENTS.md §1.2): `ida.py` exposes string search, xrefs and decompilation, and the plugin
can read bytes, but nothing in it dereferences a static slot and decodes the frozen string behind it. The REA tools
work on whole functions and would report the slot as a data reference without resolving its target. What is missing is
exactly this two-hop read, and it is small enough to write down once.
"""

import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
IMAGE_BASE = 0x140000000

# The slot in sub_140B3B7C0 that is known to name poq-app-id.
CALIBRATION = 0x1471151D0
CALIBRATION_EXPECTED = "poq-app-id"

# The slots sub_140B3B7C0 passes to sub_1408BAD40(container, key, value).
POQ_SLOTS = [
    0x147115240, 0x1471151D0, 0x146F6C400, 0x147115200,
    0x146F7CB78, 0x147115288, 0x14717E5B8, 0x146F6C498,
    0x147113F48, 0x147115310, 0x146F6C460, 0x1471795D0,
]


class Image:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.data = f.read()
        e = struct.unpack_from("<I", self.data, 0x3C)[0]
        n = struct.unpack_from("<H", self.data, e + 6)[0]
        opt = struct.unpack_from("<H", self.data, e + 20)[0]
        base = e + 24 + opt
        self.sections = []
        for i in range(n):
            off = base + i * 40
            name = self.data[off:off + 8].rstrip(b"\x00").decode("ascii", "replace")
            vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", self.data, off + 8)
            self.sections.append((name, vaddr, vsize, rawptr, rawsize))

    def file_offset(self, va):
        """VA -> file offset, or None when the VA is not backed by file bytes."""
        rva = va - IMAGE_BASE
        for _name, vaddr, vsize, rawptr, rawsize in self.sections:
            if vaddr <= rva < vaddr + max(vsize, rawsize):
                delta = rva - vaddr
                return rawptr + delta if delta < rawsize else None
        return None

    def qword(self, va):
        off = self.file_offset(va)
        if off is None or off + 8 > len(self.data):
            return None
        return struct.unpack_from("<Q", self.data, off)[0]

    def dword(self, va):
        off = self.file_offset(va)
        if off is None or off + 4 > len(self.data):
            return None
        return struct.unpack_from('<I', self.data, off)[0]

    def utf16_at(self, va, maxchars=64):
        """Read UTF-16LE starting at a VA, stopping at a NUL."""
        off = self.file_offset(va)
        if off is None:
            return None
        raw = self.data[off:off + maxchars * 2]
        text = raw.decode("utf-16-le", "replace").split("\x00")[0]
        return text

    def printable(self, text):
        if not text:
            return False
        return all(0x20 <= ord(c) <= 0x7e for c in text) and len(text) >= 2


def interpretations(img, slot):
    """Every plausible reading of a slot, with the string each yields.

    R777 settled this by looking at the bytes instead of modelling them. A slot's file content is:

        40 6a db 44 01 00 00 00 | 0a 00 00 00 | 70 00 6f 00 71 00 2d 00 ...
        └─ method table pointer ┘ └─ length ─┘ └─ UTF-16 characters ───────

    so the `off_` symbol names the string object itself: characters at +12, length as a DWORD at +8. No dereference is
    involved, and my earlier attempt failed by reading the slot's first qword as if it were an object pointer when it
    is the method table.
    """
    out = []

    def offer(label, text, length=None):
        out.append((label, text, length))

    body = img.utf16_at(slot + 12)
    length = img.dword(slot + 8)
    offer("object+12", body, length)

    # keep the older guesses so a caller can see they were tried and lost
    v = img.qword(slot)
    if v is not None and IMAGE_BASE <= v < IMAGE_BASE + 0x8000000:
        offer("deref+12", img.utf16_at(v + 12))
    return out


def calibrate(img):
    print("  calibrating on 0x%x, which should name %r" % (CALIBRATION, CALIBRATION_EXPECTED))
    for label, text, length in interpretations(img, CALIBRATION):
        ok = text == CALIBRATION_EXPECTED
        lenok = "" if length is None else (" len=%d%s" % (length, " ok" if text and length == len(text) else " MISMATCH"))
        print("    %-12s -> %r%s%s" % (label, (text or "")[:40], lenok, "   <-- MATCH" if ok else ""))
        if ok:
            return label
    print("    no interpretation reproduced it")
    return None


def main(argv):
    img = Image(EXE)
    print("  sections: " + ", ".join("%s(vaddr=0x%x)" % (n, v) for n, v, _s, _r, _z in img.sections))
    print()

    label = calibrate(img)
    if label is None:
        print("\n  stopping: without a calibrated rule the rest would be guesses")
        return 1
    print("\n  rule: %s\n" % label)

    slots = [int(a, 16) for a in argv[1:]] or POQ_SLOTS
    for slot in slots:
        text = length = None
        for lab, t, n in interpretations(img, slot):
            if lab == label:
                text, length = t, n
                break
        ok = img.printable(text) and (length is None or length == len(text))
        print("    slot 0x%-10x %-24r len=%-4s%s" % (slot, (text or "")[:22], length, "" if ok else "   (check)"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
