# Dump the ProfileCsv validation host: sub_140F74A40 registers both guard thunks
# (UnknownCountry at 0x140F77350, UnknownState at 0x140F777E0 via the same pattern).
import ida_hexrays
import json

out = {}
for ea, label in ((0x140F74A40, "csv_validator_host"),):
    cf = ida_hexrays.decompile(ea)
    out[label] = str(cf) if cf else None
    print(label, "lines:", (out[label] or "").count("\n") + 1)

with open(r"D:\projects\cyber-reverse\analysis\csv_validator_host.c", "w", encoding="utf-8") as f:
    f.write(out.get("csv_validator_host") or "")
