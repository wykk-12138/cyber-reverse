"""Runs INSIDE IDA. The construction around the notify-challenge-cmpl call site, and nothing else.

sub_141113680 is a 15,615-byte async state machine (R1126), so dumping it whole buries the answer.
This finds the line that references the URL object (0x147098688) and prints a narrow window around it,
with every set-key and verb call in that window decoded, which is how the John Lewis bodies were read.
"""
import re

import ida_bytes
import ida_hexrays

FUNC = 0x141113680
URL_OBJ = 0x147098688

TOKEN = re.compile(r"\b(?:off|unk)_147098(?:688|740|540|5E8)\b", re.I)
SETKEY = re.compile(r"sub_141FD2660\(([^,]+),\s*&(?:off|unk)_([0-9A-Fa-f]+)")
VERB = re.compile(r"sub_1408B(6310|63B0|61E0)\(([^)]*)\)")


def frozen(va):
    head = ida_bytes.get_bytes(va, 12)
    if not head or len(head) < 12:
        return None
    ln = int.from_bytes(head[8:12], "little")
    if not (0 < ln < 200):
        return None
    raw = ida_bytes.get_bytes(va + 12, ln * 2)
    if not raw or len(raw) < ln * 2:
        return None
    try:
        s = raw.decode("utf-16-le")
    except UnicodeDecodeError:
        return None
    return s if all(32 <= ord(ch) < 127 for ch in s) else None


code = str(ida_hexrays.decompile(FUNC))
lines = code.split("\n")
print("total lines:", len(lines))

hits = [i for i, ln in enumerate(lines) if "147098688" in ln]
print("URL object referenced at lines:", hits)

for h in hits:
    lo, hi = max(0, h - 30), min(len(lines), h + 6)
    print("-" * 8, "window", h)
    for i in range(lo, hi):
        s = lines[i].rstrip()
        if any(t in s for t in ("sub_141FD2660", "sub_1408B6310", "sub_1408B63B0",
                                "sub_1408B61E0", "147098688", "sub_14130D9B0", "unk_144CB7FA0",
                                "unk_144DFD730", "sub_141FD0AA0", "sub_141FD15C0")):
            print("%5d %s" % (i, s[:150]))

# Every set-key in the function whose key is one of the 3DS field names, with its bag.
print("=" * 10, "3DS-shaped keys anywhere in the function")
seen = set()
for m in SETKEY.finditer(code):
    key = frozen(int(m.group(2), 16))
    if key and any(t in key.lower() for t in ("threed", "challenge", "authenticate", "payload", "resolve")):
        if key not in seen:
            seen.add(key)
            print("   bag %-8s <- %r" % (m.group(1).strip()[:8], key))
