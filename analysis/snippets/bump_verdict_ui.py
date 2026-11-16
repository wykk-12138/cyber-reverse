import io

p = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
raw = io.open(p, "rb").read()
old = "| UI 类 | 116 个，**39 个不可达**（34%） | `UnreachedUiTypesTests` |".encode("utf-8")
new = "| UI 类 | 117 个，**39 个不可达**（33%） | `UnreachedUiTypesTests` |".encode("utf-8")
assert raw.count(old) == 1, raw.count(old)
io.open(p, "wb").write(raw.replace(old, new))
print("ok, live table row updated (116->117, 34%->33%)")
