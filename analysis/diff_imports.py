"""Dump and differ the two artifacts' import tables. (R812)

R811 explained the DLL-level difference between the original and the replica (VERSION.dll on one side, an ADVAPI32
security family on the other) but left the 29-import function-level gap unexamined. This parses both PE import
directories directly and prints the set difference, so the gap is enumerated rather than described.

Why not the rea tool: its reply for the original is large enough to be truncated in transit, and a difference computed
over a truncated set would be wrong in a way that looks precise. Reading the directories locally keeps the whole set.
"""

import struct
import sys

ORIG = r"D:\projects\cyber-reverse\target\Cybersole.exe"
REPL = r"D:\projects\cyber-reverse\replica\.publish-aot\Cybersole.Ui.exe"


def sections(data):
    e = struct.unpack_from("<I", data, 0x3C)[0]
    n = struct.unpack_from("<H", data, e + 6)[0]
    opt_size = struct.unpack_from("<H", data, e + 20)[0]
    base = e + 24 + opt_size
    out = []
    for i in range(n):
        off = base + i * 40
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, off + 8)
        out.append((vaddr, vsize, rawptr, rawsize))
    return out


def file_offset(secs, rva):
    for vaddr, vsize, rawptr, rawsize in secs:
        if vaddr <= rva < vaddr + max(vsize, rawsize):
            return rawptr + (rva - vaddr)
    return None


def cstr(data, off):
    end = data.index(b"\x00", off)
    return data[off:end].decode("ascii", "replace")


def imports(path):
    data = open(path, "rb").read()
    secs = sections(data)
    e = struct.unpack_from("<I", data, 0x3C)[0]

    # data directory 1 = imports; its offset inside the optional header depends on PE32 vs PE32+
    magic = struct.unpack_from("<H", data, e + 24)[0]
    dd = e + 24 + (112 if magic == 0x20B else 96)
    imp_rva, imp_size = struct.unpack_from("<II", data, dd + 8)

    off = file_offset(secs, imp_rva)
    if off is None:
        return {}

    result = {}
    i = 0
    while True:
        descriptor = off + i * 20
        ilt, _ts, _fwd, name_rva, iat = struct.unpack_from("<IIIII", data, descriptor)
        if ilt == 0 and name_rva == 0 and iat == 0:
            break
        dll = cstr(data, file_offset(secs, name_rva))
        thunk_rva = ilt or iat
        thunk = file_offset(secs, thunk_rva)
        fns = []
        j = 0
        while thunk is not None:
            entry = struct.unpack_from("<Q", data, thunk + j * 8)[0]
            if entry == 0:
                break
            if entry & (1 << 63):
                fns.append("#%d" % (entry & 0xFFFF))
            else:
                fns.append(cstr(data, file_offset(secs, entry + 2)))
            j += 1
        result[dll.lower()] = fns
        i += 1
    return result


def flat(d):
    out = set()
    for dll, fns in d.items():
        for f in fns:
            out.add((dll, f))
    return out


o = imports(ORIG)
r = imports(REPL)
print("  original: %d DLLs, %d imports" % (len(o), sum(len(v) for v in o.values())))
print("  replica : %d DLLs, %d imports" % (len(r), sum(len(v) for v in r.values())))

so, sr = flat(o), flat(r)
only_o = sorted(so - sr)
only_r = sorted(sr - so)
print()
print("  in original only: %d" % len(only_o))
by_dll = {}
for dll, fn in only_o:
    by_dll.setdefault(dll, []).append(fn)
for dll in sorted(by_dll):
    print("    %-34s %3d  %s" % (dll, len(by_dll[dll]), ", ".join(by_dll[dll][:6])))

print()
print("  in replica only: %d" % len(only_r))
by_dll = {}
for dll, fn in only_r:
    by_dll.setdefault(dll, []).append(fn)
for dll in sorted(by_dll):
    print("    %-34s %3d  %s" % (dll, len(by_dll[dll]), ", ".join(by_dll[dll][:6])))
