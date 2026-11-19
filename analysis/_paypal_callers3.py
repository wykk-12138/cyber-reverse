"""R1170c: the callers of the async method entries themselves.

R1170b showed 0x140a45380 / 0x140a453d0 / 0x140a27e50 are not stubs but the async methods: each one
initialises an AsyncTaskMethodBuilder, starts the state machine and reads GetResult. So the code that
awaits them - the step or action dispatcher - is one hop further up, which is what this walks.
"""
import ida_bytes
import ida_funcs
import ida_hexrays
import idautils

ENTRIES = {
    0x140A45380: "GetPurchaseUnit async method",
    0x140A27E50: "GetPaypalOrderId async method",
    0x140A453D0: "GetOrderDetails async method",
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


for fn, label in ENTRIES.items():
    print("=" * 14, label, "%#x" % fn)
    callers = []
    for r in idautils.XrefsTo(fn):
        f = ida_funcs.get_func(r.frm)
        if f and f.start_ea not in callers:
            callers.append(f.start_ea)
    print("   callers:", [hex(c) for c in callers][:8])
    for caller in callers[:3]:
        try:
            code = str(ida_hexrays.decompile(caller))
        except Exception as exc:  # noqa: BLE001
            print("   %#x decompile failed: %s" % (caller, exc))
            continue
        seen = []
        for item in idautils.FuncItems(caller):
            for ref in idautils.XrefsFrom(item, 0):
                if ref.iscode:
                    continue
                s = frozen(ref.to)
                if s and s not in seen:
                    seen.append(s)
        print("   %#x lines=%d literals=%s" % (caller, len(code.split("\n")),
                                               [x for x in seen if len(x) < 60][:10]))
    print()
