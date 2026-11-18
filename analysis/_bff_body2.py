"""Runs INSIDE IDA. For two more John Lewis BFF call sites: keys, then the mount order.

Sites from R1126: v4/orderforms/deliveries PUT at 0x140a3f650 in sub_140A3F590, and
v2/sessions/web/handover PUT at 0x140a41601 in sub_140A410E0. Body keys are the frozen strings the
containing function references; the nesting comes from the order of sub_141FD2660(bag, &key, value)
calls, which is why both are printed.
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


for label, ea in (("deliveries-v4-PUT", 0x140A3F590), ("session-handover-PUT", 0x140A410E0)):
    print("=" * 16, label, hex(ea))
    try:
        code = str(ida_hexrays.decompile(ea))
    except Exception as exc:  # noqa: BLE001
        print("   decompile failed:", exc)
        continue
    print("   -- strings referenced --")
    seen = set()
    for m in TOKEN.finditer(code):
        va = int(m.group(1), 16)
        if va in seen:
            continue
        s = frozen(va)
        if s:
            seen.add(va)
            print("   %#x  %r" % (va, s))
    print("   -- set-key order (bag <- key) --")
    for m in SETKEY.finditer(code):
        bag = m.group(1).strip()
        va = int(m.group(2), 16)
        s = frozen(va)
        print("   %-8s <- %r" % (bag[:8], s))
