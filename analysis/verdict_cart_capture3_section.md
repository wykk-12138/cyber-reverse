### 加购抓包成功：HBX 的购物车链路拿到了

`NetworkCapture` 加了 `--steps`，可以串联多个动作：

```
--steps="click:<css>; wait:<ms>; eval:<js>"
```

### 三个选择器，两次失败，第三次成

| 尝试 | 命令 | 结果 |
|---|---|---|
| 1 | `--find-add` | `totalButtons: 0` — **没滚动，页面还没渲染** |
| 2 | `--scroll --find-add` | 518 个按钮，找到 `button.atc-button` |
| 3 | `--click="button.atc-button"` | `clicked`，**但没发出任何请求** |
| 4 | `--steps="click:button.size-button; wait:800; click:button.atc-button"` | ✅ **抓到** |

第 3 次失败的原因：**HBX 的加购按钮在选尺码之前是软禁用状态**——`disabled: false`，
但点击被 JS 忽略。必须先用 `click:button.size-button` 选一个尺码。

### 抓到的端点

```
201  POST  https://hbx.com/api/v1/carts
200  POST  https://hbx.com/api/v1/carts/b338b0aa-6d38-4b64-8277-d8179a731760/items
```

**两步**：

1. `POST /api/v1/carts` → 创建空购物车，返回 cart id
2. `POST /api/v1/carts/{cartId}/items` → 往里加 variant

已落成 `HbxFlow.AddToCartAsync` / `GetCartAsync`。

**请求体是推断的**（抓包没记 body）：建购物车发 `{}`，加商品发
`{"variantId": ..., "quantity": ...}`。这一点在代码注释里写明了。

### 一个反直觉的数字

`fully covered` 从 **46 掉到 45**。

原因：`bstn` 从 `ShopifyFlow`（100%）换成 `BstnFlow`（71%）。

**这个下降是改进。** 之前那个 100% 是假的——`ShopifyFlow` 打到非 Shopify 站点，
每步都"实现"了，但每步都不工作。

**覆盖率下降可以意味着"我们终于诚实地承认有三步不知道怎么做"。**

这也是为什么覆盖率不能当"能跑"的证据：`hbx` 现在 71%，但那 71% 里
`AddToCart` 是真的（抓包验证过），而换成 `BstnFlow` 之前的 `bstn` 100% 里
`AddToCart` 是假的（打到 404）。

**同样的数字，完全不同的含义。**

---
