"""Runs INSIDE IDA. Full pseudocode of sub_140A407A0 to see which URL the PUT body goes to."""
import ida_hexrays

code = str(ida_hexrays.decompile(0x140A407A0))
for line in code.split("\n"):
    s = line.rstrip()
    if any(t in s for t in ("off_14705DC", "off_14705DA", "sub_1408B6310", "sub_1408B63B0",
                            "sub_1408B61E0", "sub_141FD2660", "sub_14130D9B0", "return")):
        print(s[:150])
