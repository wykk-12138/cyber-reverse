import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

old = "'docs\\IDB_EVIDENCE.md', 'docs\\original_view_classes.txt'"
new = "'docs\\IDB_EVIDENCE.md', 'docs\\shopify_hosts.txt', 'docs\\original_view_classes.txt'"

if old not in t:
    raise SystemExit("doc list anchor missing")

io.open(p, "w", encoding="utf-8-sig", newline="").write(t.replace(old, new, 1))
print("shopify_hosts.txt added to the doc check")
