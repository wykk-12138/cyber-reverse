"""Runs INSIDE IDA. Full pseudocode of sub_140A3FEC0 to see whether the GET and the body-less PUT
are sequential (a read-then-touch) or on different branches."""
import ida_hexrays

code = str(ida_hexrays.decompile(0x140A3FEC0))
print("total lines:", len(code.split("\n")))
for i, line in enumerate(code.split("\n")):
    print("%3d %s" % (i, line.rstrip()[:140]))
