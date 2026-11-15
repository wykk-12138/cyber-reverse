import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 84 轮。", "最后更新：第 85 轮。"),
    ("**872 通过 / 0 失败 / 2 跳过**", "**873 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R84）。", "上一次跑：全 PASS（R85）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **拼字符串的界面永远长不出第二列。**"
add = '''- **画在屏幕上的控件 = 对用户的承诺。** R84 我给 `AccountTable` 的表头画了 `⇅`，而它不排序 ——
  **上一轮修别人的死按钮，这一轮自己造了一个**。R85 把表头改成 `Button` + `SortBy()`：
  同列再点反向、换列升序、箭头 `↑/↓/⇅` 跟着变，`Ordered()` 是纯函数供测试打。
- **测试绑在实现形状上是好事。** 表头从 `TextBlock` 改成 `Button` 后，R84 的两条断言当场抛
  `First()` —— 不是脆弱，是**它正确地指出这是行为变化，不是重构**。
- **拼字符串的界面永远长不出第二列。**'''
if anchor in t and "画在屏幕上的控件 = 对用户的承诺" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
