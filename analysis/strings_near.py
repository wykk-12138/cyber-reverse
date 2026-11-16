import idautils

LO = 0x146A85000
HI = 0x146A8C000

rows = []
for s in idautils.Strings():
    if LO <= s.ea < HI:
        rows.append((s.ea, str(s)))

print("count " + str(len(rows)))
for ea, t in rows[:400]:
    print("%x\t%s" % (ea, t.replace(chr(10), " ")[:150]))
