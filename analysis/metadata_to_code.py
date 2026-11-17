"""Is there a bridge from a metadata method name to a native function address?

R1071 left two references that cannot substitute for each other: decompilation gives control flow, the metadata gives
names. A replica needs both joined, and NativeAOT has a structure for that -- reflection method records carry a native
function pointer beside the method's identity. If such a record sits near the metadata strings, then a name can be
turned into an address and the 669 decompilable functions can be labelled.

This probes rather than assumes. It reads the bytes around one metadata string that is known to exist
(Cybersole.CaptchaProviders.CaptchaProvider,Cybersole.Core.Priority!Getter at 0x1432158bc) and looks for eight-byte
little-endian values inside .text or .rdata. A hit is a candidate, not a proof; the first question is only whether
pointers live there at all.

Run: python analysis/metadata_to_code.py
"""

import struct
import sys

ROOT = r"D:\projects\cyber-reverse"
EXE = ROOT + r"\target\Cybersole.exe"
IMAGE_BASE = 0x140000000

# A metadata string that R1065/R1067 confirmed is present, and its neighbourhood.
ANCHORS = [
    (0x1432158bc, "CaptchaProvider.Priority!Getter"),
    (0x1432159dc, "CaptchaProvider.Type!Getter"),
    (0x14363e0a0, "CaptchaProvider.Priority!Property"),
]


def sections(data):
    e = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, e + 6)[0]
    opt = struct.unpack_from("<H", data, e + 20)[0]
    base = e + 24 + opt
    out = []
    for i in range(nsec):
        o = base + i * 40
        name = data[o:o + 8].rstrip(b"\0").decode("ascii", "replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", data, o + 8)
        out.append((name, va, vs, rp, rs))
    return out


def va_to_off(secs, va):
    rva = va - IMAGE_BASE
    for name, sva, svs, rp, rs in secs:
        if sva <= rva < sva + max(svs, rs):
            return rp + (rva - sva)
    return None


def in_section(secs, value, want):
    if value < IMAGE_BASE:
        return False
    rva = value - IMAGE_BASE
    for name, sva, svs, rp, rs in secs:
        if name == want and sva <= rva < sva + max(svs, rs):
            return True
    return False


def main():
    data = open(EXE, "rb").read()
    secs = sections(data)
    names = [s[0] for s in secs]
    print("  sections: %s" % ", ".join(names))

    for va, label in ANCHORS:
        off = va_to_off(secs, va)
        if off is None:
            print("  %s -> not mapped" % label)
            continue
        raw = data[off:off + 96]
        text = raw.split(b"\0")[0].decode("utf-8", "replace")
        window = data[off - 64:off + 160]
        text_hits, data_hits, other = [], [], 0
        for i in range(0, len(window) - 8, 8):
            val = struct.unpack_from("<Q", window, i)[0]
            if in_section(secs, val, ".text"):
                text_hits.append((i - 64, val))
            elif in_section(secs, val, ".rdata"):
                data_hits.append((i - 64, val))
            elif val > 0x1000:
                other += 1
        print()
        print("  === %s ===" % label)
        print("    va=0x%x  file_off=0x%x" % (va, off))
        print("    string: %s" % text[:70])
        print("    eight-byte values in a +/-window pointing into .text : **%d**" % len(text_hits))
        for delta, val in text_hits[:6]:
            print("      offset %+4d -> 0x%x" % (delta, val))
        print("    pointing into .rdata : %d     other non-small values: %d"
              % (len(data_hits), other))
    print()
    print("  → a .text hit means a code pointer sits near the metadata, which is what a reflection")
    print("    method record would carry. Hits are candidates; identity still needs the record layout.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
