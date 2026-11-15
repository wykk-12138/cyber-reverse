import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 117 轮。", "最后更新：第 118 轮。", 1)

anchor = "- **Demandware 12 步 ↔ 控制器（R117）**"
add = (
    "- **John Lewis 17 步 ↔ 12 端点（R118）**：14 步 → **9 个不同端点**，留空 3（`GetHome` 页面加载\n"
    "  + `HandleRequiresAction`/`GetStripePaymentIntent` 两次 Stripe 调用），未用端点 3。\n"
    "  **第一次「步比端点还多」** —— 端点是服务端资源、步是客户端阶段，**不要为了一一对应去拆端点**。\n"
    "- **Stripe 互补（R117+R118）**：Demandware 有 Stripe 步但**没有 Stripe 控制器**（全 Adyen）；\n"
    "  John Lewis 的 Stripe 两步**直接打 Stripe 主机**，所以没有 BFF 端点对应。\n"
    "- **有端点没步 = 还有分支没看到**（JL 的 `deliveries/delivery-address`、`v3/orderforms/payments/`）。\n"
)

if anchor in t and "John Lewis 17 步" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
