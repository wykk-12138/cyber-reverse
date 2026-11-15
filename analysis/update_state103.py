import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 102 轮。", "最后更新：第 103 轮。"),
    ("**945 通过 / 0 失败 / 2 跳过**", "**950 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R102）。", "上一次跑：全 PASS（R103）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **三族端点已收（R102）**"
add = """- **John Lewis 的 12 条摊在 v1–v4 四个 API 版本上**（R103）：账单地址 v1、支付页 v2、
  配送页 v3、收货地址 v4。**「一个 base URL + path」在这里是建模错误**，版本是数据不是常量。
  `deliveries` 与 `deliveries/`（尾斜杠）是两条独立字面量，都要记。
- **Scheels 的 cart 区有两条风控 step-up**：`sendSignifydStepUpCode` →
  `completeSignifydStepUpCheckout`。订单在码发出并被接受前不会完成；**跳过它们看起来像「一直被拒」**。
  已固化为 `RetailApiFamilies`（JohnLewisBff 12 / ScheelsFrontastic 17 / All 29）。
- **三族端点已收（R102）**"""
if anchor in t and "John Lewis 的 12 条摊在" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
