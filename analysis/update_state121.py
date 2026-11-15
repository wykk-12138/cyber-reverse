import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 120 轮。", "最后更新：第 121 轮。", 1)

anchor = "- **序号扫描不能证明归属（R120）**"
add = (
    "- **归属的证人是 lambda 字面量，不是 `d__` 连续段（R121）**：\n"
    "  `d__` 段里 `1046:GetAccessToken 1050:CartApiObjectCreate 106:AddToCartGraphQL` 是**串类**的\n"
    "  （1046/1050 属于另一个大得多的类，只是字符串相邻）；而 lambda 字面量\n"
    "  `:<CartApiObjectCreate>b__105_0 … H<GetCartAvailabilityGraphql>b__109_0` 是一条串起 105–109，\n"
    "  **这是类自己的方法表**。**池里的相邻 ≠ 同一个类。**\n"
    "- **GraphQL 购物车类（R121）**：`CartApiObjectCreate 105`、`AddToCartGraphQL 106`、\n"
    "  `AddToCartPreloadGraphQL 107`、`CreateCartGraphql 108`、`GetCartAvailabilityGraphql 109`、\n"
    "  `RefreshEmailLogin 114`。已固化为 `GraphQlCartSteps`；四条 GraphQL 调用正是 R96 缺的那半边。\n"
)

if anchor in t and "归属的证人是 lambda 字面量" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
