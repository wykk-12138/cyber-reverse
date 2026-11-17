"""Find the largest functions from .pdata alone, then decompile one.

R1045: 96.87% of this artifact's functions are sub_*, so func_query's name_contains cannot find business code. Size can.
A RUNTIME_FUNCTION in .pdata is three dwords -- begin RVA, end RVA, unwind RVA -- so the size of every function is
already in the file, no analysis needed. Sorting by that and decompiling the largest is the cheapest way to reach real
behaviour, and until this round everything came from metadata, sections and counts rather than from code.

Why not the ida plugin's own listing: func_query wants a name substring and there are no names to give it.

Run: python analysis/biggest_by_pdata.py [count]
"""

import struct
import subprocess
import sys

ROOT = r"D:\projects\cyber-reverse"
EXE = ROOT + r"\target\Cybersole.exe"
IMAGE_BASE = 0x140000000


def sections(data):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    opt_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    base = e_lfanew + 24 + opt_size
    out = {}
    for i in range(nsec):
        off = base + i * 40
        name = data[off:off + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, off + 8)
        out[name] = (vaddr, vsize, rawptr, rawsize)
    return out


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    data = open(EXE, "rb").read()
    sec = sections(data)
    if ".pdata" not in sec:
        print("  no .pdata")
        return 1
    vaddr, vsize, rawptr, rawsize = sec[".pdata"]
    blob = data[rawptr:rawptr + min(vsize, rawsize)]
    n = len(blob) // 12
    rows = []
    for i in range(n):
        begin, end, _unwind = struct.unpack_from("<III", blob, i * 12)
        if 0 < begin < end:
            rows.append((end - begin, begin))
    rows.sort(reverse=True)
    # R1071: the largest raw entries are not functions. A 687 KB entry is several functions under one RUNTIME_FUNCTION,
    # or a jump-table region, and Hex-Rays refuses it outright. Restricting to a plausible function size keeps the
    # ordering meaningful -- and the count difference already hinted at this: .pdata holds 277,094 entries where IDA
    # analyses 321,244 functions, so the two are not the same inventory.
    in_range = [(sz, begin) for sz, begin in rows if 4000 <= sz <= 30000]
    print("  runtime functions: %d   in 4k-30k: %d" % (len(rows), len(in_range)))
    print("  largest %d:" % count)
    for size, begin in in_range[:count]:
        print("    va=0x%x  size=%d bytes" % (IMAGE_BASE + begin, size))
    print()

    # decompile the top one through the plugin, which is the only part that needs IDA
    size, begin = in_range[0]
    va = IMAGE_BASE + begin
    print("  === decompiling 0x%x (%d bytes) ===" % (va, size))
    p = subprocess.run([sys.executable, "analysis/ida.py", "dec", hex(va), "--lines", "80"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    text = (p.stdout or "").strip()
    try:
        import json
        obj = json.loads(text)
        text = obj.get("pseudocode") or obj.get("code") or str(obj)[:4000]
    except Exception:
        pass
    for line in text.splitlines()[:56]:
        print("    " + line[:124])
    return 0


if __name__ == "__main__":
    sys.exit(main())
