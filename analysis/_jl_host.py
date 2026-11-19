"""R1172: which host does the John-Lewis-shaped step actually request?

R1171 left the attribution Unknown: the step table says John Lewis has GetPayPalOrderId at ordinal 37, while
the /Paypal-GetPaypalOrderId literal comes out of the SFCC Sites builder, and John Lewis serves a BFF. The
routine that awaits the order-id method (0x140a32f30, 574 lines) decides it: whatever host it names is the
store this step talks to. This prints every literal it references, hosts and paths separated.
"""
import ida_bytes
import ida_hexrays
import idautils

FUNCS = {
    0x140A32F30: "awaits GetPaypalOrderId (574 lines)",
    0x140A530F0: "awaits GetPurchaseUnit + GetOrderDetails (438 lines)",
}


def frozen(va):
    raw = ida_bytes.get_bytes(va, 12)
    if not raw or len(raw) < 12:
        return None
    ln = int.from_bytes(raw[8:12], "little")
    if not (0 < ln < 400):
        return None
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    try:
        return body.decode("utf-16-le")
    except UnicodeDecodeError:
        return None


for fn, label in FUNCS.items():
    print("=" * 16, label, "%#x" % fn)
    seen = []
    for item in idautils.FuncItems(fn):
        for ref in idautils.XrefsFrom(item, 0):
            if ref.iscode:
                continue
            s = frozen(ref.to)
            if s and s not in seen:
                seen.append(s)
    hosts = [x for x in seen if "http" in x.lower() or "/" in x and "." in x and len(x) < 80]
    print("  total literals:", len(seen))
    print("  host/path-like:")
    for x in hosts[:18]:
        print("    ", repr(x[:110]))
    print("  others:")
    for x in [y for y in seen if y not in hosts][:18]:
        print("    ", repr(x[:110]))
    print()
