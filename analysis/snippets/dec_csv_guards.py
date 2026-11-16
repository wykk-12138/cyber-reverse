# Follow the validation delegates one level deeper: the Contains() lookups inside the
# two guard functions use method tables off_1449290A0 / off_144936888. Dump their target
# code so we can see whether the lookup is ordinal/case-insensitive and which list it reads.
import ida_hexrays
import json

TARGETS = {
    "off_1449290A0": [0x147351F80, 0x147352090, 0x145148B68],
    "off_144936888": [0x14735C9A0, 0x14735CA80, 0x1451D7800],
}

out = {}
for label, eas in TARGETS.items():
    out[label] = []
    for ea in eas:
        try:
            f = ida_hexrays.decompile(ea)
            out[label].append({"ea": "0x%X" % ea, "code": str(f) if f else None})
        except Exception as exc:  # noqa: BLE001
            out[label].append({"ea": "0x%X" % ea, "error": str(exc)})

with open(r"D:\projects\cyber-reverse\analysis\csv_guard_delegates.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
for label, items in out.items():
    for it in items:
        print(label, it["ea"], "lines:", (it.get("code") or it.get("error") or "").count("\n") + 1)
