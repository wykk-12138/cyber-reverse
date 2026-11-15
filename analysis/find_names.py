# Enumerate function names / demangled names in the IDB that match a pattern.
# Usage: ida_mcp.py py find_names.py <pattern>   (pattern passed via env IDA_PATTERN)
import os, re, sys

import ida_funcs, ida_name, idautils, idaapi

pat = os.environ.get("IDA_PATTERN", "")
if not pat:
    print("IDA_PATTERN not set")
    sys.exit(1)
rx = re.compile(pat, re.I)

hits = []
total = 0
for ea in idautils.Functions():
    total += 1
    n = ida_funcs.get_func_name(ea) or ""
    d = ""
    try:
        d = ida_name.get_nice_name(ea, ida_name.GN_VISIBLE | ida_name.GN_SHORT)
    except Exception:
        pass
    if rx.search(n) or (d and rx.search(d)):
        hits.append((ea, n, d))

print("total_functions=%d  matches=%d" % (total, len(hits)))
for ea, n, d in hits[:400]:
    print("0x%x\t%s\t%s" % (ea, n, d))
