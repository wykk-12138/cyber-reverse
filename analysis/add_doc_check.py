import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

old = "'docs\\ORIGINAL_VIEWS.md', 'README.md')"
new = "'docs\\ORIGINAL_VIEWS.md', 'docs\\IDB_EVIDENCE.md', 'docs\\original_view_classes.txt', 'README.md')"
if old not in t:
    raise SystemExit("doc list anchor missing")
t = t.replace(old, new, 1)

# keep the BOM: read with utf-8-sig strips it, write it back
io.open(p, "w", encoding="utf-8-sig", newline="").write(t)
print("IDB_EVIDENCE.md added to the doc check")
