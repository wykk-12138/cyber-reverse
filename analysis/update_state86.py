import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 85 轮。", "最后更新：第 86 轮。"),
    ("**873 通过 / 0 失败 / 2 跳过**", "**887 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R85）。", "上一次跑：全 PASS（R86）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **画在屏幕上的控件 = 对用户的承诺。**"
add = '''- **常量装不下「每个任务不一样」的东西。** Nike 的 `const string Marketplace = "US"` 让
  22 个市场变成一个：无论 profile 写哪国都只能在美国结账。改成实例字段 `CountryCode` 后，
  **静态方法 `CartUrl()` 立刻编译失败** —— 编译器比人先发现「常量没了，静态也就没了」。
- **映射错了比没有映射更糟。** `NikeFlow.CountryFor` 只认二进制的 22 个市场，`UK`/`DE`/`CN`
  一律回落 US，**不凭空发明市场**——否则请求会打到一个 API 从没被问过的地方去。
- **画在屏幕上的控件 = 对用户的承诺。**'''
if anchor in t and "常量装不下「每个任务不一样」的东西" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
