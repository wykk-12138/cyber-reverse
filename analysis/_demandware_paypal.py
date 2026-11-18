"""R1162: how the image drives the three Demandware PayPal controller actions.

The image carries /Paypal-GetPurchaseUnit (0x146ab044c), /Paypal-GetPaypalOrderId?csrf_token=
(0x146ab03ec) and /Paypal-GetOrderDetails?orderId= (0x146ab0394). R1158 established that the REST
orders literal is referenced from sub_140a50cd0, whose own strings include /Paypal-GetPurchaseUnit, so
that function is the place the sequence lives. This prints, for each literal, the surrounding lines and
any verb-slot call, so the verb and the composition are observed rather than guessed.
"""
import re

import ida_bytes
import ida_hexrays

FUNC = 0x140A50CD0
TARGETS = {
    0x146AB044C - 12: "GetPurchaseUnit",
    0x146AB03EC - 12: "GetPaypalOrderId",
    0x146AB0394 - 12: "GetOrderDetails",
}
VERB = re.compile(r"sub_1408B(6310|63B0|61E0)\(")
OBJ = re.compile(r"\b(?:off|unk)_([0-9A-Fa-f]{6,})\b")


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


code = str(ida_hexrays.decompile(FUNC))
lines = code.split("\n")
print("function lines:", len(lines))

for obj, label in TARGETS.items():
    hits = [i for i, ln in enumerate(lines) if ("%X" % obj).lower() in ln.lower()]
    print("=" * 10, label, "obj %#x  referenced at %s" % (obj, hits))
    for h in hits:
        for i in range(max(0, h - 14), min(len(lines), h + 6)):
            s = lines[i].rstrip()
            mark = ">>" if i == h else "  "
            if VERB.search(s) or i == h or "off_" in s or "unk_" in s or "await" in s.lower():
                print("   %s%5d %s" % (mark, i, s[:140]))
        print()

print("=" * 10, "verb slots anywhere in the function")
for i, ln in enumerate(lines):
    for m in VERB.finditer(ln):
        name = {"6310": "PUT", "63B0": "POST", "61E0": "GET"}[m.group(1)]
        print("   %5d %s  %s" % (i, name, ln.strip()[:110]))
