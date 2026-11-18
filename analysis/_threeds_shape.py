"""Runs INSIDE IDA. Shape of the 3DS notify endpoints.

From R1145's list: notify-challenge-cmpl/ at chars 0x147098694, notify-method-cmpl at 0x14709874c,
init-challenge at 0x14709854c, init-method at 0x1470985f4. The parked note says the body keys of
notify-challenge-cmpl were never recovered, so this reads each containing function the same way the
John Lewis bodies were read: strings referenced, set-key order, and the verb slot with its third
argument (a literal 0 means no body).
"""
import re

import ida_bytes
import ida_hexrays
import idaapi
import idautils

TOKEN = re.compile(r"\b(?:off|unk)_([0-9A-Fa-f]{6,})\b")
SETKEY = re.compile(r"sub_141FD2660\(([^,]+),\s*&(?:off|unk)_([0-9A-Fa-f]+)")
VERB = re.compile(r"sub_1408B(6310|63B0|61E0)\(([^)]*)\)")

TARGETS = [
    ("notify-challenge-cmpl", 0x147098694),
    ("notify-method-cmpl", 0x14709874C),
    ("init-challenge", 0x14709854C),
    ("init-method", 0x1470985F4),
]


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


def containing(ea):
    import ida_funcs
    f = ida_funcs.get_func(ea)
    return f.start_ea if f else None


for label, chars in TARGETS:
    obj = chars - 12
    print("=" * 14, label, "chars=%#x obj=%#x" % (chars, obj))
    refs = list(idautils.XrefsTo(obj))
    print("   xrefs:", [(hex(r.frm), r.type) for r in refs][:6])
    seen_funcs = []
    for r in refs:
        fn = containing(r.frm)
        if fn and fn not in seen_funcs:
            seen_funcs.append(fn)
    print("   functions:", [hex(f) for f in seen_funcs])
    for fn in seen_funcs[:2]:
        try:
            code = str(ida_hexrays.decompile(fn))
        except Exception as exc:  # noqa: BLE001
            print("   decompile failed:", exc)
            continue
        print("   -- %#x strings --" % fn)
        done = set()
        for m in TOKEN.finditer(code):
            va = int(m.group(1), 16)
            if va in done:
                continue
            s = frozen(va)
            if s:
                done.add(va)
                print("      %#x %r" % (va, s))
        rows = list(SETKEY.finditer(code))
        print("   -- set-key order (%d) --" % len(rows))
        for m in rows:
            print("      %-8s <- %r" % (m.group(1).strip()[:8], frozen(int(m.group(2), 16))))
        for m in VERB.finditer(code):
            print("   verb slot %s args(%s)" % (m.group(1), m.group(2)))
