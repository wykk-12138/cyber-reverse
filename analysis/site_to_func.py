r"""Map disp32_scan hit sites to their containing functions via .pdata, then decompile.

WHY THIS TOOL EXISTS (AGENTS.md rule 1.2):
disp32_scan.py (this session) finds *code sites* that lea-reference frozen string objects --
something IDA does not model as xrefs (BLOCKERS §124's five probes all measured the *xref*
channel, which is empty by NativeAOT's addressing form, not the displacement bytes).
The last step -- "which function contains this site" -- needs a function table. IDA has one,
but a plain .pdata binary search is deterministic, needs no IDA session, and matches the
`RUNTIME_FUNCTION` count BLOCKERS §6/§47 already measured (277,094).

Usage:
    python analysis/site_to_func.py <site-VA> [<site-VA> ...]
"""
import io
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BINARY = os.path.join(ROOT, "target", "Cybersole.exe")


def sections(data):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    base = struct.unpack_from("<Q", data, pe + 24 + 24)[0]
    out = {}
    sec = pe + 24 + optsz
    for i in range(nsec):
        o = sec + i * 40
        name = data[o:o + 8].rstrip(b"\x00").decode()
        vsize, va, rsize, roff = struct.unpack_from("<IIII", data, o + 8)
        out[name] = (roff, rsize, base + va, vsize)
    return out


def load_pdata(data, secs):
    """RUNTIME_FUNCTION entries hold image RVAs, not section offsets (measured: adding the
    .pdata section VA produced nonsense; the end value equals base+rva of the next entry)."""
    roff, rsize, _va, _ = secs[".pdata"]
    imagebase = 0x140000000
    n = rsize // 12
    funcs = []
    blob = data[roff:roff + rsize]
    for i in range(n):
        b, e, _u = struct.unpack_from("<III", blob, i * 12)
        if b == 0:
            break
        funcs.append((imagebase + b, imagebase + e))
    funcs.sort()
    return funcs


def find(funcs, site):
    lo, hi = 0, len(funcs) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if site < funcs[mid][0]:
            hi = mid - 1
        elif site >= funcs[mid][1]:
            lo = mid + 1
        else:
            return funcs[mid]
    return None


def main(argv):
    data = io.open(BINARY, "rb").read()
    secs = sections(data)
    funcs = load_pdata(data, secs)
    print(".pdata entries: %d" % len(funcs))
    for arg in argv:
        site = int(arg, 0)
        hit = find(funcs, site)
        if hit:
            print("site 0x%X -> func 0x%X..0x%X (size %d)" % (site, hit[0], hit[1], hit[1] - hit[0]))
        else:
            print("site 0x%X -> NOT IN ANY .pdata FUNCTION" % site)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
