"""R1163: the verbs of the other two PayPal controller actions.

R1162 implemented Paypal-GetPurchaseUnit only, because that was the one whose verb an observation
covered. The other two literals live in functions this project has not walked, so this asks where each
is referenced and, for each referring function, prints any verb-slot call near the reference.
"""
import re

import ida_bytes
import ida_funcs
import ida_hexrays
import idautils

TARGETS = {
    0x146AB03EC - 12: "Paypal-GetPaypalOrderId",
    0x146AB0394 - 12: "Paypal-GetOrderDetails",
}
VERB = re.compile(r"sub_1408B(6310|63B0|61E0)\(")


def frozen(va):
    raw = ida_bytes.get_bytes(va, 12)
    if not raw or len(raw) < 12:
        return None
    ln = int.from_bytes(raw[8:12], "little")
    if not (0 < ln < 6000):
        return None
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    try:
        return body.decode("utf-16-le")
    except UnicodeDecodeError:
        return None


for obj, label in TARGETS.items():
    print("=" * 12, label, "obj %#x" % obj)
    refs = list(idautils.XrefsTo(obj))
    print("   xrefs:", [(hex(r.frm)) for r in refs][:6])
    funcs = []
    for r in refs:
        f = ida_funcs.get_func(r.frm)
        if f and f.start_ea not in funcs:
            funcs.append(f.start_ea)
    for fn in funcs[:2]:
        try:
            code = str(ida_hexrays.decompile(fn))
        except Exception as exc:  # noqa: BLE001
            print("   %#x decompile failed: %s" % (fn, exc))
            continue
        lines = code.split("\n")
        hits = [i for i, ln in enumerate(lines) if ("%X" % obj).lower() in ln.lower()]
        print("   fn %#x lines=%d literal at %s" % (fn, len(lines), hits))
        for h in hits:
            for i in range(max(0, h - 12), min(len(lines), h + 8)):
                s = lines[i].rstrip()
                if VERB.search(s) or i == h:
                    mark = ">>" if i == h else "  "
                    extra = ""
                    m = VERB.search(s)
                    if m:
                        extra = "  [" + {"6310": "PUT", "63B0": "POST", "61E0": "GET"}[m.group(1)] + "]"
                    print("   %s%5d %s%s" % (mark, i, s[:120], extra))
        for i, ln in enumerate(lines):
            if VERB.search(ln):
                print("   VERB CALL %5d %s" % (i, ln.strip()[:120]))
        print("   verb slots in fn:", [
            {"6310": "PUT", "63B0": "POST", "61E0": "GET"}[m.group(1)]
            for ln in lines for m in VERB.finditer(ln)])
