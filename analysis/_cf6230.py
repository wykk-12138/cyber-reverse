"""Runs INSIDE IDA. What does sub_141CF6230 do with a URL literal and one argument?

R1131 met it as `sub_141CF6230(&off_14705DCD8, v5)` around the John Lewis guest callback, where the URL
was never sent; here it is `sub_141CF6230(&off_147098688, v9[9])` for notify-challenge-cmpl. If it is a
concatenation helper rather than a request, then notify-challenge-cmpl has no request body at all and
the "unknown payload" is not missing evidence but evidence that there is nothing to find.
"""
import ida_hexrays

for ea in (0x141CF6230,):
    print("=" * 10, hex(ea))
    try:
        code = str(ida_hexrays.decompile(ea))
    except Exception as exc:  # noqa: BLE001
        print("decompile failed:", exc)
        continue
    lines = code.split("\n")
    print("lines:", len(lines))
    for i, ln in enumerate(lines):
        s = ln.rstrip()
        # show signature and every call/return, skipping the stack-variable prologue
        if i < 3 or any(t in s for t in ("return", "sub_", "Concat", "Append", "String",
                                          "memcpy", "::", "operator")):
            print("%4d %s" % (i, s[:150]))
