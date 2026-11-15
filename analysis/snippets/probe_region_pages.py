# Probe the fake-data region page by page using IDA's xref index (fast), instead of walking
# every instruction (which blew the plugin's 60 s budget).
import idautils
import idc

LO, HI = 0x143600000, 0x143800000
found = {}
probes = 0

for addr in range(LO, HI, 0x1000):
    probes += 1
    for xr in idautils.XrefsTo(addr, 0):
        found.setdefault(xr.frm, addr)

print("pages probed      : %d" % probes)
print("distinct refs found: %d" % len(found))
for frm in list(found.keys())[:20]:
    print("  0x%X -> 0x%X  (%s)" % (frm, found[frm], idc.get_func_name(frm) or "?"))
