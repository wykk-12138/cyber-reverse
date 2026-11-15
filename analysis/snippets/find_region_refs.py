# Find code references into the fake-data region (0x143600000..0x143800000).
# NativeAOT lays the tables out contiguously and addresses them from a base, so a per-table
# xref is empty; what matters is which functions point into the region at all.
import ida_funcs
import idautils
import idc

LO, HI = 0x143600000, 0x143800000
hits = {}
total = 0

for ea in idautils.Heads(idc.get_segm_start(idc.get_inf_attr(idc.INF_MIN_EA)),
                         idc.get_inf_attr(idc.INF_MAX_EA)):
    if not idc.is_code(idc.get_full_flags(ea)):
        continue
    for xr in idautils.XrefsFrom(ea, 0):
        if LO <= xr.to < HI:
            f = ida_funcs.get_func(ea)
            key = idc.get_func_name(f.start_ea) if f else ("0x%X" % ea)
            hits.setdefault(key, []).append((ea, xr.to))
            total += 1

print("total refs into region: %d" % total)
print("containing functions : %d" % len(hits))
for k in list(hits.keys())[:15]:
    v = hits[k]
    print("  %-56s %4d refs   first 0x%X -> 0x%X" % (k[:56], len(v), v[0][0], v[0][1]))
