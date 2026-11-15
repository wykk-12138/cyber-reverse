### `hbx` 的加购链路可复现，但前端不同步

R52 抓到过 HBX 的加购两步，这轮重跑确认它是稳定的：

```
--- steps ---
  click button.size-button -> clicked
  wait 800ms
  click button.atc-button -> clicked

201  POST https://hbx.com/api/v1/carts
200  POST https://hbx.com/api/v1/carts/999db890-9125-495b-9736-6727f67b7f10/items
```

**cart id 每次不同**（`b338b0aa…` → `999db890…`），形状一致。**端点是真的。**

### 但 mini-cart 说它是空的

点完加购后，`--find-add` 读到的 DOM 里：

```json
{"tag":"div", "id":"mini-cart",
 "text":"Your shopping bag is emptyYou have no it…",
 "cls":"mini-cart absolute border bg-white invisible hidden md:block max-w-sm"}
```

**注意 `invisible hidden`** —— mini-cart 有这两个 class，说明它**从来没被显示过**。

### 两种可能，而且能区分

| 可能 | 判据 |
|---|---|
| 加购真的成功了，只是前端没刷新 | 加购 API 返回的 body 里有商品 |
| 加购失败了（200 但 body 是错误） | 加购 API 的 body 里没有商品 |

**`NetworkCapture` 只记录请求，不记录响应体**——所以这轮分不出来。

### 但这不影响 `HbxFlow`

`HbxFlow.AddToCartAsync` 是**直接调 API**，不经过前端：

```csharp
var created = await SendJsonAsync(c, Post, ... + "/api/v1/carts", "{}", ...);
var cartId = TryRead(created.Body, "id") ?? TryRead(created.Body, "cartId");
var added = await SendJsonAsync(c, Post, ... + $"/api/v1/carts/{cartId}/items", payload, ...);
```

它自己读 `id`、自己发 item。**前端的 mini-cart 状态和它无关。**

### 所以 `hbx` 的结账后续步骤拿不到的原因是这个

要找 `/checkout`，需要：
1. 一个真实加购后的页面（mini-cart 有商品）
2. 点 mini-cart 里的 "Checkout" 按钮

而 mini-cart 在自动化点击后不显示——**所以那个按钮不存在，点不到**。

**这是「前端状态没同步」导致的，不是「站点没有那个按钮」。**

### 一个可选的绕法

`HbxFlow` 已经有 cart id，可以直接 GET 一些推测的结账路径：

```
GET /api/v1/carts/{id}/checkout
GET /api/v1/checkouts
POST /api/v1/carts/{id}/checkout
```

**但这就是 R90 刚推翻的那种猜测。** 没有对照、没有证据的路径探测，只会产生一堆 403/404
然后无法判断。

**所以停在这里是对的。** `HbxFlow` 的 `SubmitOrderAsync` 现在写的是：

```
hbx: order endpoint unknown — cart create and add are captured, checkout is not
```

**这句话准确，而且不假装知道。**

### 手写 flow 的抽查做完了

| 模块 | 结论 |
|---|---|
| `casio` | AEM + Akamai，四条根路径全 404（R89） |
| `warhammer` | 403 无差别，三条 REST 路径无证据（R90） |
| `hbx` | 加购两步验证，结账被前端状态卡住（R91） |
| `jbhifi` | 已改 ShopifyFlow，平台保证 |
| `superswipe` | App 集成，域名占位 |
| `riotgames` / `pocketgames` | 抽签流程，6/6 和 7/7 |

**七个手写 flow，三个有真 bug（都修了），四个本来就没问题。**

---
