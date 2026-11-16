"""Find which flow the OnePageCheckout plugin family belongs to. (R805)

The family carries exactly the steps casio and poq-app lack -- SetShippingAddress, SetBillingAddress, PlaceOrder -- but
a path with no owner cannot be attached to a module without guessing. Xref the strings and the caller names the store.
"""

import json
import subprocess
import sys

IDA = r"D:\projects\cyber-reverse\analysis\ida.py"

NAMES = [
    "/OnePageCheckout/CheckoutPlugin/SetShippingAddressAsync",
    "/OnePageCheckout/CheckoutPlugin/SetBillingAddressAsync",
]


def find_exact(name):
    out = subprocess.run([sys.executable, IDA, "str", name], capture_output=True, text=True)
    i = out.stdout.find("{")
    if i < 0:
        return None
    d, _ = json.JSONDecoder().raw_decode(out.stdout[i:])
    for m in d.get("matches", []):
        if m["string"].strip() == name:
            return m["addr"]
    return None


def callers(addr_hex):
    obj = int(addr_hex, 16) - 12
    out = subprocess.run([sys.executable, IDA, "xrefs", "0x%x" % obj], capture_output=True, text=True)
    i = out.stdout.find("[")
    if i < 0:
        return []
    try:
        xd, _ = json.JSONDecoder().raw_decode(out.stdout[i:])
    except Exception:
        return []
    names = []
    for row in xd:
        for x in row.get("xrefs", []):
            fn = x.get("fn") or {}
            if fn.get("addr"):
                names.append("%s(%s)" % (fn.get("name"), fn.get("size")))
    return names


for name in NAMES:
    addr = find_exact(name)
    if addr is None:
        print("  %-56s not an exact match in the pool" % name)
        continue
    print("  %-56s at %s" % (name, addr))
    c = callers(addr)
    print("      callers: %s" % (", ".join(c[:5]) if c else "(none)"))
