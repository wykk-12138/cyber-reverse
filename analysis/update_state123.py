import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 122 轮。", "最后更新：第 123 轮。", 1)

anchor = "- **证人规则很窄（R122）**"
add = (
    "- **Pop Mart 购买半边已接线（R123）**：`GetCartAsync`（shoppingCartDataList）、\n"
    "  `FetchCoupons`（coupons/list，**私有 helper 而非新 step**）、`SubmitDiscountAsync`（coupons/verify）。\n"
    "  `ClearCart` / `FetchAddress` **不实现**（端点族里没有）。\n"
    "  **行为变化：订单第一次能受购物车状态影响**（改动前从不读自己刚建的购物车）。\n"
    "  优惠券 `absent|applied|rejected` 三种都返回 Success —— 用不上的券不会让车不可下单。\n"
    "- **词表没虚方法时别发明 step**：`StoreFlow` 无 `FetchCoupons`，写成 `override` 会 CS0115；\n"
    "  行为用私有 helper 实现。另：`Profile` 只有 `Email`，券码从 `Session.Vars[\"discountCode\"]` 取。\n"
)

if anchor in t and "Pop Mart 购买半边已接线" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
