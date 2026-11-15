import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\ProxyRowTestTests.cs"
t = io.open(p, encoding="utf-8").read()

old = 'Assert.Contains("Delete", labels);'
new = 'Assert.Contains("Delete Proxies", labels);'
if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("patched delete label")

# The UI class count moved: ProxyGrid is a new class.
for path, oldc, newc in [
    (r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\PARITY.md",
     "**74 个 UI 类：24 个 `Window` 子类 + 50 个 `UserControl` 子类。**",
     "**75 个 UI 类：24 个 `Window` 子类 + 51 个 `UserControl` 子类。**"),
]:
    t2 = io.open(path, encoding="utf-8").read()
    if oldc not in t2:
        raise SystemExit("count anchor missing in " + path)
    io.open(path, "w", encoding="utf-8", newline="").write(t2.replace(oldc, newc, 1))
    print("updated count in", path)

# The mutation guard's anchor follows the same line.
p3 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tools\mutation-check.py"
t3 = io.open(p3, encoding="utf-8").read()
t3 = t3.replace('"find": "**74 个 UI 类：24 个",', '"find": "**75 个 UI 类：24 个",', 1)
t3 = t3.replace('"replace": "**74 个 UI 类：23 个",', '"replace": "**75 个 UI 类：23 个",', 1)
io.open(p3, "w", encoding="utf-8", newline="").write(t3)
print("updated mutation anchor")
