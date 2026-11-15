import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 89 轮。", "最后更新：第 90 轮。"),
    ("**897 通过 / 0 失败 / 2 跳过**", "**900 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R89）。", "上一次跑：全 PASS（R90）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **分页工具默认给你「一页」。**"
add = '''- **每取一条二进制事实，记下「这条是全的吗」。** `docs/IDB_EVIDENCE.md` 是这张账：
  事实 / 模式 / 命中 / `cursor.done` / 轮次，外加「代码常量 ↔ 数量 ↔ 哪条查询」和
  「已知取不到、别再试」。R90 复查六条全部 `done: true`（20 / 7 / 42 / 1 / 2 / 1）。
  `IDBEvidenceTests` 让文档和常量不许各自漂移；这份文档也在 `verify.ps1` 的检查清单里。
- **字符串池是字母序、跨店铺共享的。** `dump_strings.py` 的窗口摘录只能证明
  「这个字面量存在」，**不能证明「它属于 Nike」** —— `checkoutshopper-live.adyen.com`、
  `chi21120` 就和 Nike 的键挨着。
- **分页工具默认给你「一页」。**'''
if anchor in t and "每取一条二进制事实" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
