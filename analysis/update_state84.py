import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 83 轮。", "最后更新：第 84 轮。"),
    ("**868 通过 / 0 失败 / 2 跳过**", "**872 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R83）。", "上一次跑：全 PASS（R84）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **`Window` 子类不能在无头测试里构造。**"
add = '''- **拼字符串的界面永远长不出第二列。** R84 前三个账户页的数据是
  `$"{a.Host}    {a.User}    {a.InboxCount}"` —— PayPal 那行甚至把
  `running=… refreshed=…` 印在界面上。改成 `string[]` 由 `AccountTable` 按列切格，
  **数据不再为了显示而成型**。
- **`IsVisible` 在容器上，不在文字上 —— 这件事撞了两次。** R79 空态一次、R84 表头一次。
  断言「某块不见了」一律走祖先链找 `IsVisible=false`。
- **`Window` 子类不能在无头测试里构造。**'''
if anchor in t and "拼字符串的界面永远长不出第二列" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
