"""Map the modules still missing shipping/payment to their flow classes, and list DemandwareFlow's overrides."""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores"
REG = os.path.join(ROOT, "Modules", "Registry.cs")
DW = os.path.join(ROOT, "Flows", "DemandwareFlow.cs")

TARGETS = ["bstn", "casio", "fanatics", "goat", "pocketgames", "popmart", "poq-app",
           "raffle", "riotgames", "superswipe", "yeezysupply", "hypecommerce"]

reg = io.open(REG, encoding="utf-8", errors="replace").read()

# new XxxFlow("id", ...)  -- capture flow class and id, in either argument order
pattern = re.compile(r'new\s+(\w+Flow)\s*\(\s*"([\w\-]+)"')
found = {}
for m in pattern.finditer(reg):
    found.setdefault(m.group(2), []).append(m.group(1))

# also catch base-class registrations like new FlowStoreModule(new XxxFlow(...))
print("  modules -> flow class")
for t in TARGETS:
    print("    %-14s -> %s" % (t, ", ".join(found.get(t, ["(not matched)"]))))

print()
print("  every flow class used by the 63 modules:")
for k in sorted(found):
    for cls in found[k]:
        print("    %-16s %s" % (k, cls))

print()
dw = io.open(DW, encoding="utf-8", errors="replace").read()
print("  DemandwareFlow overrides:")
for line in dw.splitlines():
    if re.search(r'override\s+(async\s+)?Task<StepOutcome>|override\s+bool', line):
        print("    " + line.strip()[:100])
print("  DemandwareFlow total lines: %d" % len(dw.splitlines()))
