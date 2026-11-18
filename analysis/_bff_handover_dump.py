"""Runs INSIDE IDA. Dump sub_140A410E0 (session handover PUT) to read the bag each key lands on."""
import ida_hexrays

code = str(ida_hexrays.decompile(0x140A410E0))
for line in code.split("\n"):
    line = line.rstrip()
    if any(t in line for t in ("sub_141FD2660", "sub_141FD15C0", "sub_14130D9B0",
                               "sub_141FD31B0", "sub_141FD0AA0", "sub_1408B6310",
                               "unk_144CB7FA0", "unk_144DFD730", "unk_144DFD508")):
        print(line[:140])
