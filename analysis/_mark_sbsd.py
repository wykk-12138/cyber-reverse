import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlow.cs'
t = io.open(p, encoding='utf-8').read()
old = '        c.Session.Cookies["sbsd"] = sb;'
new = '        c.Session.Cookies["sbsd"] = sb;  // inferred: no image evidence (R297) — the pool has /sbsd and _sbsdContext, not a cookie of this name'
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('sbsd cookie marked')
