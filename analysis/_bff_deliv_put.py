"""Runs INSIDE IDA. Is the v4 deliveries PUT body-less too?

R1129 found sub_140A3F590 references only its own URL with no set-key calls. R1132 showed that a
body-less call is visible as a literal 0 in the third argument of sub_1408B6310, so this prints the
verb call plus the argument building around it.
"""
import ida_hexrays

code = str(ida_hexrays.decompile(0x140A3F590))
lines = code.split("\n")
for i, line in enumerate(lines):
    s = line.rstrip()
    if any(t in s for t in ("sub_1408B6310", "sub_1408B63B0", "sub_1408B61E0",
                            "sub_1408C22E0", "sub_143028C10")):
        print("%3d %s" % (i, s[:145]))
