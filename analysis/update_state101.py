import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 100 轮。", "最后更新：第 101 轮。"),
    ("**935 通过 / 0 失败 / 2 跳过**", "**940 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R100）。", "上一次跑：全 PASS（R101）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **Pop Mart 是一整套"
add = """- **Nike 的结账步骤不是 REST 子路径，是 persisted GraphQL（R101 的关键发现）**：
  `checkouts/internal/graphql/persisted?operationName=` + {CheckoutExtensionSessionToken,
  PaypalDetails, PaypalToken, PollForReceipt, Proposal, SubmitForCompletion}。
  **这就是 R87/R88 找不到 `buy/orders/v2/{id}/shipping` 的原因 —— 它不存在。**
  但 6 个名字 ≠ 14 个步骤，**映射仍然空白**，别当成答案。
- **SFCC 有两条路**：经典 `/on/demandware.store/Sites-{site}-Site/{locale}/{controller}`
  （`DemandwareFlow`）与 **SCAPI** `/scapi/ShopperBaskets/*` + `/scapi/ShopperLogin/*`
  （9 个端点，R101 固化为 `ScapiEndpoints`）。replica 原来只有前者。
- **路径字面量可以按前缀聚类**：`python analysis/path_families101.py` 会把 16,404 条路径
  收成 1,817 个前缀，一眼看出还有哪些族没做（`/rpc/ec`、`/component/singlepagecheckout`、
  `/apps/gatekeeper/api`、`checkout.johnlewis.com/bff`、`apihub.scheels.com/frontastic`）。
- **Pop Mart 是一整套"""
if anchor in t and "persisted GraphQL（R101" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
