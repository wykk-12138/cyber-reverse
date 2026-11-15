import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 116 轮。", "最后更新：第 117 轮。", 1)

anchor = "- **Pop Mart 24 步 ↔ 39 端点（R116）**"
add = (
    "- **Demandware 12 步 ↔ 控制器（R117）**：连了 10 对，留空 2（`GetPaymentMethod`、\n"
    "  `CreateStripePaymentMethod`）。**缺的三个控制器是我的表缺，不是二进制缺** ——\n"
    "  再搜一次就找到 `CheckoutServices-SubmitBilling` / `CheckoutShippingServices-UpdateShippingMethod` /\n"
    "  `CheckoutServices-PaymentAuthorization` / `FetchOrderModel` / `SubmitCash` + Adyen 家族。\n"
    "  **独立结论：镜像里没有任何 `Stripe-*` 控制器，支付控制器全是 Adyen 的。**\n"
)

if anchor in t and "Demandware 12 步" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
