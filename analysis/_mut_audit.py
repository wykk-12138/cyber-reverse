import io, re, importlib.util, sys
spec = importlib.util.spec_from_file_location("mc", r"D:\projects\cyber-reverse\replica\tools\mutation-check.py")
mc = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mc)   # safe: main() only runs under __main__
except SystemExit:
    pass
print('mutations:', len(mc.MUTATIONS))
missing, ok = [], 0
for m in mc.MUTATIONS:
    try:
        text = io.open(m["file"], encoding="utf-8").read()
    except FileNotFoundError:
        missing.append((m["name"], "FILE MISSING"))
        continue
    if m["find"] in text:
        ok += 1
    else:
        missing.append((m["name"], "anchor not found"))
print('anchors present:', ok, '/', len(mc.MUTATIONS))
for n, why in missing:
    print('  DEAD:', n.replace('—','-'), '->', why)
