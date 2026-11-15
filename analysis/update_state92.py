import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 91 轮。", "最后更新：第 92 轮。"),
    ("**904 通过 / 0 失败 / 2 跳过**", "**905 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R91）。", "上一次跑：全 PASS（R92）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **空结果不是「没有信息」。**"
add = """- **店铺名以「类型名 + `0x1b 0x08` 后缀」存放**，带 `$` 锚点的正则会漏掉它们；
  `^[A-Z]\\w+(Handler|Tester)$` 只能确认某个店存在，**不足以枚举全部店铺**（53 条里绝大多数是框架类名）。
- **同一个店的身份也写在 User-Agent 里。** `OFFSPRING/3 … poq.ios/21.1.6 poq-webview` ⇒
  OffSpring 是 **Poq** 移动 App，不是 Magento —— replica 的 `offspring → MagentoFlow` 没有依据。
- **空结果不是「没有信息」。**"""
if anchor in t and "店铺名以「类型名" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
