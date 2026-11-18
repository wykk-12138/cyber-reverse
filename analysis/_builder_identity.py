"""R1164: does the GET actually carry the builder the controller path was appended to?

R1163 implemented the two order lookups on the strength of "the containing function has exactly one verb
slot, and it is a GET", and said plainly in the code that the builder identity was not traced. This reads
the lines between the append and the call in both functions so that either the pairing becomes an
observation or the gap stays open with a concrete reason.
"""
import ida_hexrays

CASES = [
    (0x140A31E40, 0x146AB03E0, "Paypal-GetPaypalOrderId", 118, 152),
    (0x140A51E20, 0x146AB0388, "Paypal-GetOrderDetails", 110, 145),
]

for fn, obj, label, lo, hi in CASES:
    print("=" * 14, label, "fn %#x" % fn)
    code = str(ida_hexrays.decompile(fn))
    lines = code.split("\n")
    for i in range(max(0, lo), min(len(lines), hi)):
        s = lines[i].rstrip()
        mark = ">>" if ("%X" % obj).lower() in s.lower() or "1408B61E0" in s else "  "
        print("  %s%5d %s" % (mark, i, s[:150]))
    print()
