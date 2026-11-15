"""Function-pointer runs, read straight from the PE instead of from an IDA database. (R636)

**Why this exists when `ida.py` already measured the same tables** (project convention §1.2 requires saying so):

The run census in `BLOCKERS` §51 was produced through `analysis/ida.py py`, which needs the original's `.i64`
(1.4 GB) open with about 2 GB of private memory. This session hit `available = 1.7 GB` after the machine had been
running builds all day, and the project's own memory discipline says not to open that database in that state.
So the same question is answered from the file alone.

**What replaces IDA**: `IMAGE_DIRECTORY_ENTRY_EXCEPTION` (`.pdata`) is a first-class PE structure that lists one
`RUNTIME_FUNCTION` per non-leaf function, keyed by its begin RVA. That is an **authoritative** function-start set --
not a heuristic -- so "a qword that points at a function start" can be decided without a disassembler.

**What is therefore different from §51, and must not be conflated**:
  * §51 counted runs whose targets are **IDA `af`-analysed function starts** (321,244 functions).
  * This counts runs whose targets are in **`.pdata`** (~one entry per non-leaf function; leaf functions have none).
  * A leaf function reached by a pointer is counted by §51 and missed here. So this under-counts targets, and the
    two run counts are comparable in shape but not identical in definition.

Read-only. Prints a census; writes nothing.
"""

import struct
import sys

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"


def parse_pe(data):
    if data[:2] != b"MZ":
        raise SystemExit("not a PE: no MZ")
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_off:pe_off + 4] != b"PE\0\0":
        raise SystemExit("not a PE: no PE signature")

    coff = pe_off + 4
    (machine, nsect, _, _, _, opt_size, _) = struct.unpack_from("<HHIIIHH", data, coff)
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    if magic != 0x20B:
        raise SystemExit("expected PE32+ (magic 0x20B), got 0x%X" % magic)

    image_base = struct.unpack_from("<Q", data, opt + 24)[0]
    dirs_off = opt + 112

    sections = []
    sec_off = opt + opt_size
    for i in range(nsect):
        base = sec_off + i * 40
        name = data[base:base + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, base + 8)
        chars = struct.unpack_from("<I", data, base + 36)[0]
        sections.append({
            "name": name, "vsize": vsize, "vaddr": vaddr,
            "rawsize": rawsize, "rawptr": rawptr, "chars": chars,
        })

    return image_base, dirs_off, sections


def rva_to_off(sections, rva):
    for s in sections:
        if s["vaddr"] <= rva < s["vaddr"] + max(s["vsize"], s["rawsize"]):
            delta = rva - s["vaddr"]
            if delta < s["rawsize"]:
                return s["rawptr"] + delta
    return None


def main():
    with open(PATH, "rb") as fh:
        data = fh.read()

    image_base, dirs_off, sections = parse_pe(data)
    print("image base   : 0x%X" % image_base)
    print("sections     : %d" % len(sections))

    for s in sections:
        kind = "code" if s["chars"] & 0x20000000 else ("exec" if s["chars"] & 0x20000000 else "data")
        print("  %-10s vaddr 0x%08X  vsize %10d  raw %10d  %s" %
              (s["name"], s["vaddr"], s["vsize"], s["rawsize"],
               "X" if s["chars"] & 0x20000000 else "-"))

    # .pdata -- exception directory
    exc_rva, exc_size = struct.unpack_from("<II", data, dirs_off + 3 * 8)
    print()
    print("exception dir: rva 0x%X  size %d  -> %d RUNTIME_FUNCTION entries"
          % (exc_rva, exc_size, exc_size // 12))

    off = rva_to_off(sections, exc_rva)
    starts = set()
    if off is not None:
        for i in range(exc_size // 12):
            begin = struct.unpack_from("<I", data, off + i * 12)[0]
            if begin:
                starts.add(begin)
    print("distinct function starts from .pdata: %d" % len(starts))

    if not starts:
        raise SystemExit("no .pdata starts parsed; refusing to report a run census")

    lo, hi = min(starts), max(starts)
    print("pdata start range: 0x%08X .. 0x%08X" % (lo, hi))

    # scan data sections for runs of qwords whose RVA is a function start
    runs = []          # (section, length, first_rva_of_run)
    total_qwords = 0
    targets = set()
    for s in sections:
        if s["chars"] & 0x20000000:
            continue                                  # skip executable section
        if s["rawsize"] == 0 or s["vaddr"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        n = len(body) // 8
        cur = 0
        run_qwords = 0
        for i in range(n):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            rva = va - image_base if va >= image_base else None
            if rva is not None and rva in starts:
                if cur == 0:
                    run_first = s["vaddr"] + i * 8
                cur += 1
                run_qwords += 1
                total_qwords += 1
                targets.add(rva)
            else:
                if cur:
                    runs.append((s["name"], cur, run_first))
                cur = 0
        if cur:
            runs.append((s["name"], cur, run_first))

    print()
    print("runs of >=1 pointer to a .pdata start:")
    print("  runs           : %d" % len(runs))
    print("  qwords in runs : %d" % total_qwords)
    print("  distinct targets in runs: %d" % len(targets))

    # the earlier census only counted runs of >= 8
    for threshold in (2, 4, 8, 16, 32):
        sel = [r for r in runs if r[1] >= threshold]
        print("  runs >= %-3d : %6d   qwords %8d" %
              (threshold, len(sel), sum(r[1] for r in sel)))

    from collections import Counter
    bucket = Counter()
    for _name, length, _first in runs:
        if length >= 64:
            bucket["64+"] += 1
        elif length >= 32:
            bucket["32-63"] += 1
        elif length >= 16:
            bucket["16-31"] += 1
        elif length >= 8:
            bucket["8-15"] += 1
        elif length >= 4:
            bucket["4-7"] += 1
        else:
            bucket["1-3"] += 1
    print()
    print("run-length distribution:")
    for k in ("1-3", "4-7", "8-15", "16-31", "32-63", "64+"):
        print("  %-6s %6d" % (k, bucket[k]))

    per_section = Counter(name for name, _l, _f in runs if _l >= 8)
    print()
    print("sections holding runs >= 8:")
    for name, count in per_section.most_common():
        print("  %-10s %6d" % (name, count))


if __name__ == "__main__":
    sys.exit(main())
