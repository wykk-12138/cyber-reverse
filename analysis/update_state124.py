import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 123 轮。", "最后更新：第 124 轮。", 1)

anchor = "- **Pop Mart 购买半边已接线（R123）**"
add = (
    "- **Demandware 双路不是两条完整路径（R124）**：15 步切成三段 —— App 有端点 3（`getAccessToken`、\n"
    "  `addItemToBasket`）、Dw 有端点 3（`Cart-Get`、`Cart-AddProduct`）、**App 无端点 4**\n"
    "  （`ApplyDiscountApp`、`GetCheckoutApp`、`GetRatesApp`、`SubmitOrderApp`）。\n"
    "  **关键事实：SCAPI 族里没有下单端点**（6 个 ShopperBaskets + 2 个 ShopperLogin），\n"
    "  所以 app 路只到购物车，必须切回经典控制器结账下单。`SubmitOrderAsync` 只有经典路径是对的。\n"
)

if anchor in t and "Demandware 双路不是两条完整路径" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
