"""Runs INSIDE IDA. Prints the pseudocode of the two POST bodies so the nesting can be read."""
import ida_hexrays

for label, ea in (("billing-address", 0x140A424B0), ("deliveries-details", 0x140A428D0)):
    print("=" * 16, label, hex(ea))
    try:
        code = str(ida_hexrays.decompile(ea))
    except Exception as exc:  # noqa: BLE001
        print("   decompile failed:", exc)
        continue
    for line in code.split("\n"):
        print("   " + line.rstrip()[:150])
