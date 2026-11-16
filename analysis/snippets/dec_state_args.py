# The last unknown in the State chain: sub_141CF6BF0 formats the error with TWO args
# (sub_142D3D750(&v3, fmt, &v4, 2)), where v4 = sub_141D1FDF0(arg). Decompile that plus
# the country_error_sink's format call (sub_141DA1FC0) argument meaning, and identify the
# singleton qword_1472C7440 / qword_1472C7460 by walking their EEType chains.
import ida_hexrays

out = {}
for ea, label in ((0x141D1FDF0, "state_arg2_builder"), (0x141CF6230, "column_getter")):
    try:
        cf = ida_hexrays.decompile(ea)
        out[label] = str(cf) if cf else None
    except Exception as exc:  # noqa: BLE001
        out[label] = "ERR " + str(exc)
    print(label, "lines:", (out[label] or "").count("\n") + 1)

with open(r"D:\projects\cyber-reverse\analysis\csv_state_args.c", "w", encoding="utf-8") as f:
    for k, v in out.items():
        f.write("==== %s ====\n%s\n\n" % (k, v or ""))
print("wrote csv_state_args.c")
