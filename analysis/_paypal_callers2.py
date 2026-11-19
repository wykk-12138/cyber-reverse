"""R1170b: one level above the async plumbing, where the awaiting method lives.

R1170 found each PayPal controller machine has three callers: a 5-line thunk, a ~37-line MoveNext and a
stub. Those are compiler-generated. The method that actually awaits the async body is the caller of the
stub, so this walks there and prints the stub's callers together with their short literals - which is
where a step or action name would sit.
"""
import ida_bytes
import ida_funcs
import ida_hexrays
import idautils

STUBS = {
    0x142B35920: "GetPurchaseUnit stub",
    0x142B2DA00: "GetPaypalOrderId stub",
    0x142B35B20: "GetOrderDetails stub",
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


for fn, label in STUBS.items():
    print("=" * 14, label, "%#x" % fn)
    callers = []
    for r in idautils.XrefsTo(fn):
        f = ida_funcs.get_func(r.frm)
        if f and f.start_ea not in callers:
            callers.append(f.start_ea)
    print("   callers:", [hex(c) for c in callers][:6])
    for caller in callers[:3]:
        f = ida_funcs.get_func(caller)
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
        short = [x for x in seen if len(x) < 60]
        print("   %#x lines=%d literals=%s" % (caller, len(code.split("\n")), short[:10]))
    print()
