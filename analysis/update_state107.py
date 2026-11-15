import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 106 轮。", "最后更新：第 107 轮。"),
    ("**965 通过 / 0 失败 / 2 跳过**", "**970 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R106）。", "上一次跑：15/16 PASS（R107，见下）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **协议层（R106）**"
add = """- **SFCC 双路径已落地（R107）**：`DemandwareFlow.AddToCartAsync` 门开在 `scapi.token` 上 ——
  有 token 走 `/scapi/ShopperBaskets/createBasket` + `addItemToBasket?siteId=`，
  失败 `return null` 回落经典 `Cart-AddProduct`。`DemandwareDualPathTests` 五条钉住
  「门 → SCAPI → 经典」的顺序、`return null` 回落、Bearer 头在 try/finally，
  以及**同一个类里不许出现第二份 `SiteId`**（第一次编译就撞了 CS0102）。
- **`NikeKasadaFlowTests.TheFlowProducesARealToken…` 在 `-Full` 里会挂、单跑必过**
  （两轮验证同一条；单跑 3/3 通过 15 s）。它是实时 Kasada 取脚本测试，慢测并行阶段超时。
  **不要把它当成回归**；判断法：单跑 + 看是否只有这一条。
- **协议层（R106）**"""
if anchor in t and "SFCC 双路径已落地（R107）" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
