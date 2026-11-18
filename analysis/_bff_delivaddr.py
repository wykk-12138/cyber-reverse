"""Runs INSIDE IDA. Keys + mount order for the v4 delivery-address PUT.

Site from R1126: v4/orderforms/deliveries/delivery-address PUT at 0x140a43e03 in sub_140A43A80.
Also reports whether the verb call's body argument is the literal 0 (a body-less call), which is how
R1132/R1133 distinguished "keys live elsewhere" from "there is no body".
"""
import re

import ida_bytes
import ida_hexrays

TOKEN = re.compile(r"\b(?:off|unk)_([0-9A-Fa-f]{6,})\b")
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


code = str(ida_hexrays.decompile(0x140A3F750))
print("-- strings --")
seen = set()
for m in TOKEN.finditer(code):
    va = int(m.group(1), 16)
    if va in seen:
        continue
    s = frozen(va)
    if s:
        seen.add(va)
        print("   %#x  %r" % (va, s))
print("-- set-key order --")
rows = list(SETKEY.finditer(code))
if not rows:
    print("   (none)")
for m in rows:
    print("   %-8s <- %r" % (m.group(1).strip()[:8], frozen(int(m.group(2), 16))))
print("-- verb calls --")
for m in VERB.finditer(code):
    print("   slot %s args(%s)" % (m.group(1), m.group(2)))
