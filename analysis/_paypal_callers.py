"""R1170: who calls the three PayPal controller machines?

The three functions are known (0x140a50cd0 for GetPurchaseUnit, 0x140a31e40 for GetPaypalOrderId,
0x140a51e20 for GetOrderDetails) but nothing in the replica calls the matching methods, and for three
rounds the answer has been "no sequence evidence". A caller usually carries the step or action name, so
this walks one level up: the xrefs to each function entry, the caller's own literals, and whether the
caller is a dispatcher (many callees) or a single step.
"""
import ida_bytes
import ida_funcs
import ida_hexrays
import idautils

TARGETS = {
    0x140A50CD0: "GetPurchaseUnit machine",
    0x140A31E40: "GetPaypalOrderId machine",
    0x140A51E20: "GetOrderDetails machine",
}


def frozen(va):
    raw = ida_bytes.get_bytes(va, 12)
    if not raw or len(raw) < 12:
        return None
    ln = int.from_bytes(raw[8:12], "little")
    if not (0 < ln < 200):
        return None
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    try:
        return body.decode("utf-16-le")
    except UnicodeDecodeError:
        return None


for fn, label in TARGETS.items():
    print("=" * 14, label, "%#x" % fn)
    callers = []
    for r in idautils.XrefsTo(fn):
        f = ida_funcs.get_func(r.frm)
        if f and f.start_ea not in callers:
            callers.append(f.start_ea)
    print("   distinct callers:", [hex(c) for c in callers][:6])
    for caller in callers[:2]:
        f = ida_funcs.get_func(caller)
        callees = set()
        body = ida_bytes.get_bytes(f.start_ea, f.end_ea - f.start_ea) or b""
        for r in idautils.XrefsFrom(f.start_ea):
            pass
        try:
            code = str(ida_hexrays.decompile(caller))
        except Exception as exc:  # noqa: BLE001
            print("   caller %#x decompile failed: %s" % (caller, exc))
            continue
        print("   caller %#x lines=%d" % (caller, len(code.split("\n"))))
        # its literals: strings it points at, short ones only
        seen = []
        for item in idautils.FuncItems(caller):
            for ref in idautils.XrefsFrom(item, 0):
                if ref.iscode:
                    continue
                # a frozen object is at ref.to; its chars start 12 bytes later
                s = frozen(ref.to)
                if s and s not in seen:
                    seen.append(s)
        print("   literals:", [x for x in seen if len(x) < 70][:14])
    print()
