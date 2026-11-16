import re

p = r"D:/projects/cyber-reverse/replica/docs/baseline/recovered_async_methods.txt"
lines = []
with open(p, "r", encoding="utf-8", errors="replace") as f:
    for ln in f:
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.startswith("#"):
            continue
        parts = ln.split()
        if len(parts) >= 2 and parts[1].isdigit():
            lines.append((parts[0], int(parts[1])))

print("pairs: " + str(len(lines)))

# company: which method names appear as the FIRST step of some ordinal run?
names = set(n for n, c in lines)
for probe in ("Start", "Init", "GetHome", "CheckVerification", "SubmitSaleRegistration"):
    print("  %-24s in baseline: %s" % (probe, probe in names))

# any name starting with Start or Init
starts = sorted(n for n in names if n.startswith("Start"))
inits = sorted(n for n in names if n.startswith("Init"))
print("")
print("Start* (%d): %s" % (len(starts), ", ".join(starts[:30])))
print("")
print("Init*  (%d): %s" % (len(inits), ", ".join(inits[:30])))
