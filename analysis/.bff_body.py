"""One-shot: decompile a function, then decode every frozen string it references.

The two POST sites found in R1126 are billing-address (POST at 0x140a427c1 in 0x140a424b0) and
deliveries/details (POST at 0x140a42abd in 0x140a428d0). Their verbs are known but their request
bodies are not, and a body's key names are exactly what a frozen-string sweep of the containing
function can recover. Every candidate is read with the NativeAOT layout
[MethodTable*:8][Length:4][UTF-16 chars] and only plausible printable payloads are printed.
"""
import json
import re
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import ida  # noqa: E402

import ida_bytes  # noqa: E402


def dec(addr):
    raw = ida.call("decompile", {"addr": addr})
    text = raw if isinstance(raw, str) else json.dumps(raw)
    try:
        return json.JSONDecoder().raw_decode(text)[0].get("code") or ""
    except json.JSONDecodeError:
        return ""


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


TOKEN = re.compile(r"\b(?:off|unk)_([0-9A-Fa-f]{6,})\b")

for label, func in (("billing-address", "0x140a424b0"), ("deliveries/details", "0x140a428d0")):
    code = dec(func)
    print("=" * 18, label, func, "code bytes:", len(code))
    if not code:
        print("   <no pseudocode>")
        continue
    seen = []
    for m in TOKEN.finditer(code):
        va = int(m.group(1), 16)
        if va in [v for v, _ in seen]:
            continue
        s = frozen(va)
        if s:
            seen.append((va, s))
    if not seen:
        print("   <no decodable frozen strings among referenced constants>")
    for va, s in seen:
        print("   %#x  %r" % (va, s))
