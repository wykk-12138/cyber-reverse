import idautils

LO = 0x14337B000
HI = 0x14337CE00

rows = []
for s in idautils.Strings():
    if LO <= s.ea < HI:
        rows.append((s.ea, str(s)))

rows.sort()
print("count " + str(len(rows)))
for ea, t in rows:
    clean = t.replace(chr(10), " ").replace(chr(0), "")
    print("%x\t%s" % (ea, clean[:120]))
