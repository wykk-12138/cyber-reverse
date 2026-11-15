import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\verify.ps1"
t = io.open(p, encoding="utf-8-sig").read()

old = "'docs\\IDB_EVIDENCE.md', 'docs\\shopify_hosts.txt'"
new = "'docs\\IDB_EVIDENCE.md', 'docs\\ENDPOINT_FAMILIES.md', 'docs\\shopify_hosts.txt'"

if old not in t:
    raise SystemExit("doc list anchor missing")

io.open(p, "w", encoding="utf-8-sig", newline="").write(t.replace(old, new, 1))
print("ENDPOINT_FAMILIES.md added to the doc check")
