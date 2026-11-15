import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 88 轮。", "最后更新：第 89 轮。"),
    ("**895 通过 / 0 失败 / 2 跳过**", "**897 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R88）。", "上一次跑：全 PASS（R89）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **Nike 14 步的子路径：当前证据不可达，别再试。**"
add = '''- **分页工具默认给你「一页」。** R86 用 `find_regex "Nike [A-Z]{2}"`（limit 40）只取到
  从 `IT` 开始的一段，写下「22 个市场」；R89 读掉 `cursor.done` 才看到 **42 个**（`AT`…`ZA`，
  字母序，0x28 字节间隔）。**凡是能分页的地方，「读到的」和「全部」永远是两件事。**
  后果不是「少几项」：`CountryFor("UK")` 因为「二进制没有 GB 市场」回落到 US，
  **把英国用户送去美国结账**，而且还有一条测试把错误钉住了。
- **测试保证「代码和信念一致」，不保证「信念和原版一致」。** 那条
  `Assert.Equal("US", CountryFor("UK"))` 在错误事实上完全正确地运行。
- **Nike 14 步的子路径：当前证据不可达，别再试。**'''
if anchor in t and "分页工具默认给你「一页」" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
