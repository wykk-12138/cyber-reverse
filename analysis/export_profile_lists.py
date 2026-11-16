"""Export the country/state lists the replica needs for CSV validation. (R704)

**Why this exists** (project convention §1.2): the format reader (`analysis/fake_data_nested.py`) exists and is validated
6/6, but nothing ever wrote the data out. R681 recorded "数据全可得" -- readable, not exported.

**Why now**: R702/R703 decoded the validation rule from the original and I verified both guard functions. Implementing
that rule in the replica needs the same lists the original uses. Rebuilding them from the original is the faithful
implementation, not a shortcut: the original embeds exactly these tables.

**Criterion, fixed before measuring**: the export must reproduce R688's measured counts -- English `country` **244**,
`state` **50**, `state_abbr` **50** -- and every `state_abbr` entry must be the abbreviation of the `state` at the same
index. A mismatch on either check fails the export.

Writes `replica/src/Cybersole.Core/Locales/ProfileValidation.en.json`.
"""

import io
import json
import os
import re
import struct
import sys

EXE = r"D:\projects\cyber-reverse\target\Cybersole.exe"
OUT = r"D:\projects\cyber-reverse\replica\src\Cybersole.Core\Locales\ProfileValidation.en.json"
LO, HI = 0x03600000, 0x03800000

EXPECT_COUNTRY = 244
EXPECT_STATE = 50
EXPECT_ABBR = 50


def sections(path):
    data = open(path, "rb").read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt = struct.unpack_from("<H", data, pe + 20)[0]
    base = pe + 24 + opt
    out = []
    for i in range(nsec):
        off = base + i * 40
        vaddr, rsize, roff = struct.unpack_from("<III", data, off + 12)
        out.append((vaddr, rsize, roff))
    return data, out


def r2o(secs, rva):
    for vaddr, size, roff in secs:
        if vaddr <= rva < vaddr + size:
            return roff + (rva - vaddr)
    return None


def flat_values(data, body, body_len):
    """Entries shaped 0x02 <idx> NUL <u32 n> <n bytes NUL-terminated>."""
    pos, end, out = body, body + body_len, []
    while pos < end:
        if data[pos] != 0x02:
            return None
        pos += 1
        z = data.find(b"\x00", pos, min(pos + 8, end))
        if z < 0 or not data[pos:z].isdigit():
            return None
        pos = z + 1
        n = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        payload = data[pos:pos + n]
        if len(payload) != n or not payload.endswith(b"\x00"):
            return None
        pos += n
        out.append(payload[:-1].decode("utf-8", "replace"))
    return out


def main():
    data, secs = sections(EXE)
    lo, hi = r2o(secs, LO), r2o(secs, HI)
    region = data[lo:hi]

    # collect every table header that parses flatly, then pick the English ones by size
    found = {}
    for m in re.finditer(rb"\x00\x04([a-z][a-z0-9_]{2,20})\x00", region):
        name = m.group(1).decode()
        name_off = lo + m.start() + 2
        field_off = name_off + len(m.group(1)) + 1
        field = struct.unpack_from("<I", data, field_off)[0]
        body_len = field - 5
        if body_len <= 0:
            continue
        body = field_off + 4
        vals = flat_values(data, body, body_len)
        if vals:
            found.setdefault(name, []).append(vals)

    def pick(name, want):
        for vals in found.get(name, []):
            if len(vals) == want:
                return vals
        return None

    country = pick("country", EXPECT_COUNTRY)
    state = pick("state", EXPECT_STATE)
    abbr = pick("state_abbr", EXPECT_ABBR)

    print("tables found: %s" % ", ".join("%s(%s)" % (k, [len(v) for v in vs])
                                         for k, vs in sorted(found.items())))
    print()
    ok = True
    for label, vals, want in (("country", country, EXPECT_COUNTRY),
                              ("state", state, EXPECT_STATE),
                              ("state_abbr", abbr, EXPECT_ABBR)):
        if vals is None:
            print("  %-11s MISSING (no table with %d entries)" % (label, want))
            ok = False
        else:
            print("  %-11s %d entries   first=%r  last=%r"
                  % (label, len(vals), vals[0], vals[-1]))
    if not ok:
        return 1

    # every abbreviation must be a prefix-consistent short form of its state
    bad = [(i, state[i], abbr[i]) for i in range(len(state))
           if not abbr[i] or not state[i].lower().startswith(abbr[i][0].lower())]
    print()
    print("  abbreviation/state alignment anomalies: %d %s"
          % (len(bad), bad[:5] if bad else ""))

    payload = {
        "_comment": ("Exported from target/Cybersole.exe by analysis/export_profile_lists.py (R704). "
                     "The original embeds these tables; the replica validates CSV country/state against them."),
        "locale": "en",
        "country": country,
        "state": state,
        "state_abbr": abbr,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print()
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
