import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\GlobalPrune.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        "__nativeMask", "__nativeMaskInstalled", "__patchJournal", "__windowBaseline",'''
new = ('''        "__nativeMask", "__nativeMaskInstalled", "__patchJournal", "__windowBaseline", "__topList",
        "__globalPrune", "__documentPrune",''')

if old not in t:
    raise SystemExit("keep anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("keep list extended")
