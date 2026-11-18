"""R1141: look for standalone state-machine type-name objects.

ida.py str failed when the pattern carried angle brackets, so this queries the string cache directly
inside IDA and reports every address whose payload contains the token, which is the question that
matters: does '<PlaceOrder>d__36' exist as its own frozen string (and therefore has a traceable xref),
or only inside the concatenated enumeration found in R1135?
"""
import ida_bytes
import idaapi
import ida_nalt  # noqa: F401

PATTERNS = ["PlaceOrder>d__36", "SubmitOrder>d__33", "PlaceOrder>b__36", "AuthenticatePayment>d__34"]


def frozen(va):
    head = ida_bytes.get_bytes(va, 12)
    if not head or len(head) < 12:
        return None
    ln = int.from_bytes(head[8:12], "little")
    if not (0 < ln < 400):
        return None
    raw = ida_bytes.get_bytes(va + 12, ln * 2)
    if not raw or len(raw) < ln * 2:
        return None
    try:
        return raw.decode("utf-16-le")
    except UnicodeDecodeError:
        return None


# Walk the string list the plug-in builds, the same one ida.py str reads.
import idautils
import ida_strlist  # noqa: F401

count = 0
ida_strlist.build_strlist()
for si in idautils.Strings():
    count += 1
    s = str(si)
    for p in PATTERNS:
        if p in s:
            print("%-28s at %#x len=%d : %r" % (p, si.ea, si.length, s[:120]))
            break
print("strings walked:", count)
