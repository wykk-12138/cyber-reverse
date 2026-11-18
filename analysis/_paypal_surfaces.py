"""R1158: who calls the two PayPal surfaces?

The replica has two parallel PayPal paths - the REST orders API (PayPalGateway.TokenizeAsync /
AuthorizeAsync, https://www.paypal.com/v2/checkout/orders) and the web 3DS machine
(PayPalThreeDs.RunAsync / ContinueAsync, the graphql + payment-authentication family). Only the REST
side is wired into the gateway interface; RunAsync has no caller at all.

Before deciding where RunAsync belongs, the question is which subsystem each surface serves in the
image. That is decidable: take the object address of each frozen literal, ask for its xrefs, map them to
containing functions, and print a nearby error string from each function so the subsystem names itself.
"""
import ida_bytes
import ida_funcs
import ida_hexrays
import idautils

# chars_va from R1145/R1147 readings, so the object is chars-12
REST_CHARS = 0x14709910C      # https://www.paypal.com/v2/checkout/orders
GQL_CHARS = 0x147097E78       # https://www.paypal.com/graphql/
THREEDS_CHARS = 0x147098540   # .../payment-authentication/threeds/v1/init-challenge


def frozen(va):
    raw = ida_bytes.get_bytes(va, 12)
    if not raw or len(raw) < 12:
        return None
    ln = int.from_bytes(raw[8:12], "little")
    if not (0 < ln < 5000):
        return None
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    try:
        return body.decode("utf-16-le")
    except UnicodeDecodeError:
        return None


def subsystem(fn_ea, limit=6):
    """A few readable strings from the function, which usually name the subsystem."""
    try:
        code = str(ida_hexrays.decompile(fn_ea))
    except Exception:  # noqa: BLE001
        return []
    out, seen = [], set()
    import re

    for m in re.finditer(r"\b(?:off|unk)_([0-9A-Fa-f]{6,})\b", code):
        va = int(m.group(1), 16)
        if va in seen:
            continue
        s = frozen(va)
        if s and 3 <= len(s) <= 70 and s.isprintable():
            seen.add(va)
            out.append(s)
        if len(out) >= limit:
            break
    return out


for label, chars in (("REST orders", REST_CHARS), ("graphql", GQL_CHARS),
                     ("threeds/init-challenge", THREEDS_CHARS)):
    obj = chars - 12
    print("=" * 12, label, "obj %#x" % obj)
    refs = list(idautils.XrefsTo(obj))
    funcs = []
    for r in refs:
        f = ida_funcs.get_func(r.frm)
        if f and f.start_ea not in funcs:
            funcs.append(f.start_ea)
    print("   xrefs:", len(refs), "functions:", [hex(f) for f in funcs])
    for fn in funcs[:3]:
        print("   -- %#x: %s" % (fn, subsystem(fn)))
