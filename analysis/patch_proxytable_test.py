import io

# The proxy table test no longer has a FillProxyTable() to look for; the page reloads itself.
p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\ProxyTableTests.cs"
t = io.open(p, encoding="utf-8").read()

old = 'var fills = all.Contains("FillProxyTable()", StringComparison.Ordinal);'
new = 'var fills = all.Contains("Reload()", StringComparison.Ordinal);'
if old not in t:
    raise SystemExit("anchor 1 missing")
t = t.replace(old, new, 1)

old2 = 'Assert.True(fills, "the subscriber does not rebuild the table");'
new2 = 'Assert.True(fills, "the subscriber does not rebuild the page");'
if old2 in t:
    t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched ProxyTableTests")
