import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 121 轮。", "最后更新：第 122 轮。", 1)

anchor = "- **归属的证人是 lambda 字面量，不是 `d__` 连续段（R121）**"
add = (
    "- **证人规则很窄（R122）**：八个流程里只有 **Nike（41–58）** 与 **John Lewis（20–39）** 有归属证人；\n"
    "  Pop Mart / Demandware ×2 / CollectPlus / StructureToken ×2 **没有** —— 它们的缺口保持未解。\n"
    "  **名字会重名，序号不会跨类**：序号 1 的 `Authorize` 不是 Nike 序号 42 的那个。\n"
    "- **Pop Mart 有两半（R122 第二个独立证据）**：24 步抽签 flow + **6 方法购物车类**\n"
    "  （`GetCartDataList 1`、`FetchCoupons 2`、`SubmitDiscount 3`、`ClearCart 4`、`FetchAddress 5/6` 重载），\n"
    "  与 `/shop/v1/*` 逐一对应。已固化为 `PopMartCartSteps`。\n"
)

if anchor in t and "证人规则很窄" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
