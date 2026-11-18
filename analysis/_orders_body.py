"""Runs INSIDE IDA. Keys, mount order and verb for sub_140A40F20 -- the only function that references
the bff/v2/orders literal (chars 0x14705d7cc, object 0x14705d7c0, data xref at 0x140a40fac)."""
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


code = str(ida_hexrays.decompile(0x140A40F20))
print("chars:", len(code))
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
