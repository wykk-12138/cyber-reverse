r"""Resolve any `off_` / `unk_` data address the decompiler emits into its frozen object.

WHY THIS TOOL EXISTS (AGENTS.md rule 1.2):
`ida.py dec` emits data references as opaque `off_/unk_` names. On this NativeAOT image every
one of them that points into the frozen-string region carries `[mt:8][len:4][utf16]`. Decoding
them by hand (BLOCKERS §35's layout rule) is mechanical; this does it and also names the
MethodTable when it is one of the few we have already identified.

Usage:
    python analysis/names_at.py <VA> [<VA> ...]
"""
import io
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BINARY = os.path.join(ROOT, "target", "Cybersole.exe")

DATA_FILE = 0x6A45C00
DATA_VA = 0x146A47000
RDATA_FILE = 0x314D200
RDATA_VA = 0x14314E000
RDATA_SZ = 0x38F8A00


def read_at(data, va, n):
    if DATA_VA <= va < DATA_VA + 0x9C1000:
        fo = DATA_FILE + (va - DATA_VA)
    elif RDATA_VA <= va < RDATA_VA + RDATA_SZ:
        fo = RDATA_FILE + (va - RDATA_VA)
    else:
        return None
    return data[fo:fo + n]


def main(argv):
    data = io.open(BINARY, "rb").read()
    for arg in argv:
        va = int(arg, 0)
        b = read_at(data, va, 8 + 4 + 256)
        if b is None:
            print("0x%X  (outside mapped data)" % va)
            continue
        mt = struct.unpack_from("<Q", b, 0)[0]
        ln = struct.unpack_from("<i", b, 8)[0]
        if 0 < ln <= 128:
            ch = b[12:12 + ln * 2].decode("utf-16-le", "replace")
            if ch.isprintable():
                print("0x%X  str  mt=0x%X len=%d %r" % (va, mt, ln, ch))
                continue
        # else: dump the first qwords
        qs = struct.unpack_from("<QQQ", b, 0)
        print("0x%X  raw  %s" % (va, " ".join("0x%X" % q for q in qs)))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
