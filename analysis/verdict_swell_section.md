### Yeezy 是 Swell 店铺，那 150 行手写实现全是猜的

`YeezySupplyFlow` 原来是一个 150 行的 `StoreFlow` 直系：Akamai 队列、从 `/queue`
抓 `queueToken`、HTML 里正则挖 `variantId`/`sku`/`size`、POST 时带 token。

**实测发现这些全都不存在**：

```
GET  https://yzy-prod.swell.store/api/settings      <- Swell
GET  https://yzy-prod.swell.store/api/cart          <- Swell
GET  https://yeezy.com/api/geo
POST https://yeezy.com/cdn-cgi/challenge-platform/…  <- Cloudflare，不是 Akamai
```

**Swell** 是一个 headless 电商平台，前端是 SvelteKit。关键点是：

> **购物车 API 在 `yzy-prod.swell.store`，和店铺域名是两个 host。

所以往 `yeezy.com/api/cart` 发请求永远不会成功——**它不在那个域上**。

### 同时发现 `yeezysupply.com` 已死

旧域名解析但没有任何内容（5 个请求，全空）。已把 `Domains` 改成只有 `yeezy.com`。

### 重写后的 `YeezySupplyFlow`

| 项 | 状态 |
|---|---|
| `/api/settings`、`/api/cart` on swell host | ✅ 已验证 |
| Cloudflare 在前面 | ✅ 已验证 |
| 商品路径与 cart-item 路径 | ⚠️ 按 Swell 文档形状写，未抓包 |
| 结账 | ❌ Swell 是 hosted checkout，无法从这里提交 |

加购的 404 处理特意写成：

> `"yeezy: /api/cart POST not found — Swell path differs from the documented shape; needs a click-through capture"`

——**不是"网络错误"，是"我知道这条路可能不对，并且知道该用什么方法确认"。**

### 这轮的账

| 模块 | 平台 | 定性 |
|---|---|---|
| `yeezysupply` | **Swell**（`yzy-prod.swell.store`） | ✅ 重写 |
| `superswipe` | 自建 `relay.superswipe.com` | 已定性，未改 |
| `fanatics` | Akamai 403 | 拿不到 |
| `hypecommerce` | GoDaddy 停放 | 死域名，已记录 |

### 一个可复用的判据

这轮的发现过程很干净：

1. 抓首页 → 看到 `yzy-prod.swell.store`
2. 认出 Swell → 知道它的 API 在平台子域
3. 改 `Domains`，重写 flow 指向那个子域

**关键在第 2 步**：把"一个陌生的 host"认成"一个已知平台"。这比逐条猜端点有效得多——
认出来之后，整套 API 形状都是公开知识。

前七次平台误判也都是靠这个：认出 `/on/demandware.store/` 是 Demandware、
认出 `/cart.js` 是 Shopify、认出 `/api/beast/` 是 BSTN 自建。

---
