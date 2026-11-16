# Walk the xaml:Bind chain for the Authenticate button:
#   sub_140765730 (UI build) -> sub_1407BC810 (binding ctor wrapper)
#   -> ? -> the delegate that invokes Authenticate when the command executes.
# Dump the call chain from the binding ctor's method table and the UI-build function's
# direct callees that are near it in address space (same compilation unit).
import json

import ida_hexrays
import idaapi
import idautils
import idc

out = {"callers": {}, "callees": {}}


def callees(ea):
    res = []
    f = idaapi.get_func(ea)
    if not f:
        return res
    for h in idautils.FuncItems(f.start_ea):
        for xref in idautils.CodeRefsFrom(h, 0):
            res.append(xref)
    return sorted(set(res))


for ea in (0x1407BC810,):
    out["callees"]["0x%X" % ea] = ["0x%X" % x for x in callees(ea)]

# who calls 0x1407BC810 and 0x140765730?
for target in (0x1407BC810, 0x140765730, 0x140765440, 0x14076D2F0):
    callers = ["0x%X" % x for x in idautils.CodeRefsTo(target, 0)]
    out["callers"]["0x%X" % target] = callers

with open(r"D:\projects\cyber-reverse\analysis\license_chain.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
