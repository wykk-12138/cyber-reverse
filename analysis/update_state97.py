import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 96 轮。", "最后更新：第 97 轮。"),
    ("**916 通过 / 0 失败 / 2 跳过**", "**922 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R96）。", "上一次跑：全 PASS（R97）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **PDB 这条路断了（R96）**"
add = """- **照抄也会被自己的洁癖改坏（R97）**：Shopify 的购物车查询片段在镜像里**以 `"` 开头**、
  **花括号 12 开 13 关**（它是片段，开头 `)` 关掉了 `cart(…)`，文档收尾的 `}` 在、开头的 `{` 不在）。
  写测试断言「配平」会逼着人把忠实抄本改错 —— 要显式记账，不要整齐。
- **Shopify GraphQL 链路已落代码但未接通**：`ShopifyGraphQl` 有 354/346 字符的两份逐字文档、
  四个 API 版本、`checkoutUrl` 深度解析；**没有 storefront token 就不会真调用**，这条线是 inert 的。
- **PDB 这条路断了（R96）**"""
if anchor in t and "照抄也会被自己的洁癖改坏" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
