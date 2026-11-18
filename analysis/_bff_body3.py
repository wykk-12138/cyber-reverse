"""Runs INSIDE IDA. Keys + mount order for GuestCallback (v4 PUT) and deliveries/ (v4 GET).

Sites from R1126: v4/callback/guest PUT at 0x140a40921 in sub_140A407A0, and
v4/orderforms/deliveries/ GET at 0x140a3fbef in sub_140A3FB10.
"""
import re

import ida_bytes
import ida_hexrays

TOKEN = re.compile(r"\b(?:off|unk)_([0-9A-Fa-f]{6,})\b")
SETKEY = re.compile(r"sub_141FD2660\(([^,]+),\s*&(?:off|unk)_([0-9A-Fa-f]+)")


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


for label, ea in (("guest-callback-PUT", 0x140A407A0), ("deliveries-slash-GET", 0x140A3FB10)):
    print("=" * 16, label, hex(ea))
    try:
        code = str(ida_hexrays.decompile(ea))
    except Exception as exc:  # noqa: BLE001
        print("   decompile failed:", exc)
        continue
    print("   -- strings --")
    seen = set()
    for m in TOKEN.finditer(code):
        va = int(m.group(1), 16)
        if va in seen:
            continue
        s = frozen(va)
        if s:
            seen.add(va)
            print("   %#x  %r" % (va, s))
    print("   -- set-key order --")
    rows = list(SETKEY.finditer(code))
    if not rows:
        print("   (none)")
    for m in rows:
        s = frozen(int(m.group(2), 16))
        print("   %-8s <- %r" % (m.group(1).strip()[:8], s))
