import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 124 轮。", "最后更新：第 125 轮。", 1)

anchor = "- **Demandware 双路不是两条完整路径（R124）**"
add = (
    "- **第六个流程：Adyen/PayPal 快捷结账（R125）**：六步 33–38（`AdyenSession`、\n"
    "  `SubmitPaymentPayPal`、`AdyenPayPalPatchOrder`、`GetPayPalAccessToken`、\n"
    "  `AdyenSaveExpressShopperDetails`、`ShowConfirmationPaymentFromComponent`）。\n"
    "  字面量首 token `<PlaceOrder>d__32` **属于前一条字符串**，去掉才是 6 步连续。\n"
    "  **与 R124 相反：这条路能在一侧走完。**\n"
    "- **`/scapi/` 确认只有 9 条**（7 ShopperBaskets + 2 ShopperLogin，无下单无优惠券）。\n"
    "- **补进两个控制器**：`Adyen-SaveExpressShopperDetails`、`ShopperInfo-IP`\n"
    "  （前者会话里从未出现过 —— 与 R117 同型的「窗口外还有东西」）。\n"
)

if anchor in t and "第六个流程：Adyen/PayPal" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
