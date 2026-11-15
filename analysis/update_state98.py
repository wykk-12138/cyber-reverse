import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 97 轮。", "最后更新：第 98 轮。"),
    ("**922 通过 / 0 失败 / 2 跳过**", "**923 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R97）。", "上一次跑：全 PASS（R98）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **照抄也会被自己的洁癖改坏（R97）**"
add = """- **`StepOutcome` 是 struct**：`StepOutcome?` 是 `Nullable<T>`，`return graph!` 报 CS0266，
  必须 `return graph.Value`。**`!` 只对引用类型的可空标注说话。**
- **GraphQL 已接进 `ShopifyFlow.GetCartAsync`，门开在 token 上**：有
  `shopify.storefrontToken` + `shopify.cartId` 才发请求，否则回落 `/cart.js`；
  请求失败返回 null 让调用方回落，**不把「这家店没给 token」报成结账失败**。
- **照抄也会被自己的洁癖改坏（R97）**"""
if anchor in t and "StepOutcome` 是 struct" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
