import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 99 轮。", "最后更新：第 100 轮。"),
    ("**930 通过 / 0 失败 / 2 跳过**", "**935 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R99）。", "上一次跑：全 PASS（R100）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **抽签链路（R99）**"
add = """- **Pop Mart 是一整套 `/shop/v1/*`（39 个端点）**（R100）：`box_set/preview` → `box_set/extract` →
  `boxCart/addBoxListToCart` → `order/pre/v2/buyNow`，再加四家收银台
  `cash/desk/{adyen,alipayGlobal,paypal,stripe}/pay`。已固化为 `PopMartEndpoints`；
  replica 原来的 `/api/stock`、`/api/cart/add`、`/api/order/submit` **三个都不存在**。
- **「看起来合理、实际属于另一个家族」在本会话犯了五次**：Nike `buy/orders/v2`（R87）、
  BSTN `/api/beast`（R91）、Demandware `Checkout-Submit*`（R94）、Shopify `cart/change.js`（R96）、
  Pop Mart `/api/*`（R100）。**同一个错误五次 = 方法问题**：顺序必须是
  **先 dump 字符串、再写代码**，不是先写再找证据背书。
- **抽签链路（R99）**"""
if anchor in t and "Pop Mart 是一整套" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
