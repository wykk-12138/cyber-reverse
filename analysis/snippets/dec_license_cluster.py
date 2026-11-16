# Decompile the LicenseControl function cluster and resolve every data reference.
# Snippet runs inside IDA via analysis/run_idapy.py (file-based, avoids shell escaping).
import json
import re

import ida_hexrays
import ida_name
import idaapi

FUNCS = [
    ("0x140765440", "InitializeComponent_a"),
    ("0x140765730", "LicenseControl_main"),
    ("0x14076D2F0", "cluster_c"),
    ("0x14076BA00", "xaml_loader"),
]

out = []
for addr_s, label in FUNCS:
    ea = int(addr_s, 16)
    cf = ida_hexrays.decompile(ea)
    code = str(cf) if cf else "<decompile failed>"
    out.append({"func": addr_s, "label": label, "lines": code.count("\n") + 1,
                "code": code})

with open(r"D:\projects\cyber-reverse\analysis\license_control_decomp.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("wrote license_control_decomp.json; funcs: %d" % len(out))
for o in out:
    print(o["func"], o["label"], o["lines"], "lines")
