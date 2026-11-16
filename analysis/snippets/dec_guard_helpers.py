# The guard sub_140F752D0 takes a2 (a boxed string) and returns a lookup table row.
# It: boxes a2 -> sub_141CFA390 (ToLowerInvariant? trim?) -> sub_142E74840 with off_1449290A0
# (a Contains/FindFirst delegate table) against qword_1472C7440 (a singleton with TWO lists:
# +8 tried first, falls back to +0). Dump what qword_1472C7440 is and what sub_141CFA390 does,
# plus the off_1449290A0 method-table name via its EEType pointer chain.
import ida_hexrays
import idc
import json

out = {}
for ea, label in ((0x141CFA390, "string_normalise"), (0x142E74840, "list_lookup"),
                  (0x141CF6EA0, "country_error_sink"), (0x141CF6BF0, "state_error_sink")):
    try:
        cf = ida_hexrays.decompile(ea)
        out[label] = str(cf) if cf else None
    except Exception as exc:  # noqa: BLE001
        out[label] = "ERR " + str(exc)
    print(label, "lines:", (out[label] or "").count("\n") + 1)

with open(r"D:\projects\cyber-reverse\analysis\csv_guard_helpers.c", "w", encoding="utf-8") as f:
    for k, v in out.items():
        f.write("==== %s ====\n%s\n\n" % (k, v or ""))
print("wrote csv_guard_helpers.c")
