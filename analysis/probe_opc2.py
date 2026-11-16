"""Resolve the off_ slots referenced by the SetBillingAddress caller, to find which store it serves. (R806)

R805 found a third checkout surface -- /OnePageCheckout/CheckoutPlugin/{SetShippingAddress, SetBillingAddress,
SetGuestEmail, SetGiftWrapping} plus /Checkout/PlaceOrder -- with two callers and no owner. The caller must reference
some store identity: a host, a client slug, or a module id. Read every string slot it touches and see.
"""

import json
import subprocess
import sys

IDA = r"D:\projects\cyber-reverse\analysis\ida.py"
BASE = 0x140000000


def dec(addr, lines=120):
    out = subprocess.run([sys.executable, IDA, "dec", hex(addr), "--lines", str(lines)],
                         capture_output=True, text=True)
    i = out.stdout.find("{")
    if i < 0:
        return {}
    d, _ = json.JSONDecoder().raw_decode(out.stdout[i:])
    return d


def read_slot(obj_addr):
    """off_x names the string object: +8 dword length, +12 UTF-16 chars."""
    out = subprocess.run([sys.executable, IDA, "xrefs", hex(obj_addr)], capture_output=True, text=True)
    return None


d = dec(0x140D6AAA0)
code = d.get("code") or ""
print("  total_lines:", d.get("total_lines"), " code chars:", len(code))
print()

slots = []
for line in code.splitlines():
    s = line.strip()
    if "off_14" in s or "unk_14" in s:
        for tok in s.replace(",", " ").replace("(", " ").replace(")", " ").split():
            if tok.startswith(("off_14", "unk_14")) and tok not in slots:
                slots.append(tok)
    if "sub_14" in s:
        pass

print("  string slots referenced: %d" % len(slots))
for t in slots:
    print("    " + t)

print()
print("  lines mentioning a slot or a call:")
for line in code.splitlines():
    s = line.strip()
    if "off_14" in s or "unk_14" in s:
        print("    " + s[:112])
