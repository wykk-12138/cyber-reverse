"""Runs INSIDE IDA. Two open questions from R1131/R1126.

1. sub_140A3FB10 (v4/orderforms/deliveries/ GET) also references '/methods' (0x146ab5dd0) -- is that
   concatenated onto the URL (a derived endpoint) or used for something else?
2. sub_140A3FEC0 carries BOTH the payment-page GET (site 0x140a3ff44) and a PUT (site 0x140a4003b):
   what does the PUT side send?
Print only the lines that show URL construction, key setting and verb calls.
"""
import ida_hexrays

WANT = ("off_14705DB98", "off_146AB5DD0", "off_14705D6B4", "sub_1408C22E0", "sub_141FD2660",
        "sub_14130D9B0", "sub_141CF6230", "sub_1408B6310", "sub_1408B63B0", "sub_1408B61E0",
        "off_14705DC", "off_1470")

for label, ea in (("deliveries-slash-GET", 0x140A3FB10), ("payment-page", 0x140A3FEC0)):
    print("=" * 16, label, hex(ea))
    try:
        code = str(ida_hexrays.decompile(ea))
    except Exception as exc:  # noqa: BLE001
        print("   decompile failed:", exc)
        continue
    for line in code.split("\n"):
        s = line.rstrip()
        if any(t in s for t in WANT):
            print("   " + s[:150])
