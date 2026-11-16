import idautils

LO = 0x143380300
HI = 0x143380900

rows = []
for s in idautils.Strings():
    if LO <= s.ea < HI:
        rows.append((s.ea, str(s)))

print("count " + str(len(rows)))
for ea, t in rows[:200]:
    print("%x\t%s" % (ea, t.replace(chr(10), " ")[:160]))
