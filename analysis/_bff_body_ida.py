"""Runs INSIDE IDA (via analysis/ida.py py). Decompiles a function and decodes its frozen strings.

The two POST sites from R1126 are billing-address (POST at 0x140a427c1 in sub_140a424b0) and
deliveries/details (POST at 0x140a42abd in sub_140a428d0). Their verbs are evidenced; their request
bodies are not. A body's key names are frozen strings referenced by the containing function, so this
decompiles the function and decodes every off_/unk_ constant under the NativeAOT layout
[MethodTable*:8][Length:4][UTF-16 chars].
"""
import re

import ida_bytes
import ida_hexrays
import idaapi

TOKEN = re.compile(r"\b(?:off|unk)_([0-9A-Fa-f]{6,})\b")


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


for label, ea in (("billing-address", 0x140A424B0), ("deliveries-details", 0x140A428D0)):
    print("=" * 16, label, hex(ea))
    try:
        code = str(ida_hexrays.decompile(ea))
    except Exception as exc:  # noqa: BLE001
        print("   decompile failed:", exc)
        continue
    found, seen = [], set()
    for m in TOKEN.finditer(code):
        va = int(m.group(1), 16)
        if va in seen:
            continue
        s = frozen(va)
        if s:
            seen.add(va)
            found.append((va, s))
    print("   pseudocode chars:", len(code), " distinct frozen strings:", len(found))
    for va, s in found:
        print("   %#x  %r" % (va, s))
