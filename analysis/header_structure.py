"""Is there common structure in the 363 headers at `table_base - 0x18`? (R639)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636: 1.7-2.4 GB free
against a 1.4 GB `.i64`). Same file-only route.

**Discrimination criteria, fixed BEFORE measuring** -- this session has eight cases where a criterion was written too
narrow and reported absence where something existed, so the rule comes first and the numbers second:

For each of the 3 qwords in the header, classify the slot as:

  * **FLAG**   -- the slot takes at most 8 distinct values across the 363 headers (a type tag / flags word)
  * **POINTER** -- at least 90% of the slot's values fall inside one section's address range
  * **ZERO**   -- at least 90% of the headers have 0 in that slot
  * **MIXED**  -- none of the above: high cardinality with no range concentration

A header family is declared to have **common structure** only if at least one slot is FLAG, POINTER or ZERO.
If all three slots are MIXED, the answer is **no common structure** and the 0x18 header stays address arithmetic.

Read-only. Prints; writes nothing.
"""

import struct
import sys
from collections import Counter

PATH = r"D:\projects\cyber-reverse\target\Cybersole.exe"
MIN_RUN = 32
HEADER = 0x18


def parse_pe(data):
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    coff = pe_off + 4
    (_m, nsect, _t, _d, _p, opt_size, _c) = struct.unpack_from("<HHIIIHH", data, coff)
    opt = coff + 20
    image_base = struct.unpack_from("<Q", data, opt + 24)[0]
    sections = []
    sec = opt + opt_size
    for i in range(nsect):
        b = sec + i * 40
        name = data[b:b + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, b + 8)
        chars = struct.unpack_from("<I", data, b + 36)[0]
        sections.append({"name": name, "vsize": vsize, "vaddr": vaddr,
                         "rawsize": rawsize, "rawptr": rawptr, "chars": chars})
    return image_base, opt + 112, sections


def rva_to_off(sections, rva):
    for s in sections:
        if s["vaddr"] <= rva < s["vaddr"] + max(s["vsize"], s["rawsize"]):
            d = rva - s["vaddr"]
            if d < s["rawsize"]:
                return s["rawptr"] + d
    return None


def which_section(sections, rva):
    for s in sections:
        if s["vaddr"] <= rva < s["vaddr"] + s["vsize"]:
            return s["name"]
    return "?"


def main():
    data = open(PATH, "rb").read()
    image_base, dirs_off, sections = parse_pe(data)

    exc_rva, exc_size = struct.unpack_from("<II", data, dirs_off + 3 * 8)
    off = rva_to_off(sections, exc_rva)
    starts = {struct.unpack_from("<I", data, off + i * 12)[0] for i in range(exc_size // 12)}
    starts.discard(0)

    tables = []
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        cur = 0
        run_at = 0
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            rva = va - image_base if va >= image_base else None
            if rva is not None and rva in starts:
                if cur == 0:
                    run_at = s["vaddr"] + i * 8
                cur += 1
            else:
                if cur >= MIN_RUN:
                    tables.append((run_at, cur))
                cur = 0
        if cur >= MIN_RUN:
            tables.append((run_at, cur))

    # headers = tables whose base-0x18 is itself referenced
    values = set()
    for s in sections:
        if s["chars"] & 0x20000000 or s["rawsize"] == 0:
            continue
        body = data[s["rawptr"]:s["rawptr"] + s["rawsize"]]
        for i in range(len(body) // 8):
            va = struct.unpack_from("<Q", body, i * 8)[0]
            if va >= image_base:
                values.add(va - image_base)

    heads = []
    for base, count in tables:
        h = base - HEADER
        if h in values:
            o = rva_to_off(sections, h)
            if o is not None and o + HEADER <= len(data):
                q = struct.unpack_from("<QQQ", data, o)
                heads.append((h, count, q))

    print("tables >= %d : %d" % (MIN_RUN, len(tables)))
    print("headers referenced at base-0x%X : %d" % (HEADER, len(heads)))
    if not heads:
        raise SystemExit("no referenced headers; nothing to classify")

    print()
    print("first 6 headers:")
    for h, count, q in heads[:6]:
        print("  0x%08X n=%-4d  %s" % (h, count, tuple(hex(x) for x in q)))

    print()
    verdicts = []
    for slot in range(3):
        vals = [q[slot] for _h, _c, q in heads]
        distinct = len(set(vals))
        zero_share = sum(1 for v in vals if v == 0) / len(vals)
        inside = Counter()
        for v in vals:
            if v >= image_base:
                inside[which_section(sections, v - image_base)] += 1
        top_share = (max(inside.values()) / len(vals)) if inside else 0.0
        top_name = max(inside, key=inside.get) if inside else "-"

        if distinct <= 8:
            kind = "FLAG"
        elif zero_share >= 0.9:
            kind = "ZERO"
        elif top_share >= 0.9:
            kind = "POINTER"
        else:
            kind = "MIXED"
        verdicts.append(kind)

        print("slot %d: distinct=%-6d zero=%4.0f%%  top-section=%-8s %4.0f%%  -> %s"
              % (slot, distinct, zero_share * 100, top_name, top_share * 100, kind))
        if distinct <= 8:
            print("        values: %s" % sorted(set(vals))[:8])

    print()
    if any(v in ("FLAG", "ZERO", "POINTER") for v in verdicts):
        print("VERDICT: common structure present -- slots classified as %s" % verdicts)
    else:
        print("VERDICT: all three slots MIXED -- no common structure; 0x18 stays address arithmetic")


if __name__ == "__main__":
    sys.exit(main())
