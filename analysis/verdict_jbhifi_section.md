### 换方向后第一个小时：又抓到一个平台误判

上一轮决定停止投 BSTN，转去验"只对 mock 验证过"的那批模块。先看它们的平台。

### 四个"一步下单"店铺的实际状况

| 模块 | 探测结果 |
|---|---|
| `jbhifi` | **Shopify**（`/cart.js` → `{"token":…,"items":[…]}`）+ 独立 OAuth |
| `fanatics` | **Akamai 403**（`_es_/fo/ping/`），拿不到 |
| `hypecommerce` | **GoDaddy 停放页** —— 死域名 |
| `superswipe` | 自建 `relay.superswipe.com` |

### `jbhifi` 是第七个平台误判

原来是一个手写的 `StoreFlow`，往 `/api/cart/add` 和 `/api/checkout/submit` 发请求。

实测：

```
GET /cart.js                       -> 200, 303 B, Shopify cart 对象
/.well-known/shopify/monorail/     -> 页面加载时就调
```

**店面是 Shopify，那两条 `/api/` 路由不存在。**

但 `JbHiFiFlow` 里的 OAuth 是真的——JB Hi-Fi 用 `auth.jbhifi.com.au/oauth/token`。
**Shopify Plus 大客户挂自建账号系统，这两件事可以同时成立。**

改法：变成 `ShopifyFlow` 的子类，**只保留 `LoginAsync`**。

```csharp
public sealed class JbHiFiFlow : ShopifyFlow
{
    public JbHiFiFlow() : base("jbhifi", "JB Hi-Fi", new[] { "jbhifi.com.au" }) { }

    public override bool RequiresAccount => true;
    public override async Task<StepOutcome> LoginAsync(...)   // 保留 OAuth
}
```

覆盖矩阵从 71%（假）变成 **100%（真）**。

### `hypecommerce` 记进死域名

`hypecommerce.com` 是 GoDaddy 的 **reseller 停放页**，`hypecommerce.io` 同运营方、无店面。

已加进 `DomainClaimTests` 的 knownDead 列表（现在 6 条）。

### 七个平台误判的完整清单

| 模块 | 原注册 | 实际 |
|---|---|---|
| `hbx` | ShopifyFlow | 自建 `/api/v2/` |
| `converse` | ShopifyFlow | Demandware |
| `bstn` | ShopifyFlow | 自建 `/api/beast/` |
| `footpatrol` | MagentoFlow | Shopify |
| `size` | MagentoFlow | Shopify |
| `funko` | site id `Funko-Site` | `FunkoUS-Site` |
| **`jbhifi`** | **手写 StoreFlow + `/api/cart/add`** | **Shopify + 独立 OAuth** |

### 一个观察

`jbhifi` 这个和前六个不同：**它不是"用错了平台类"，而是"手写了一个平台已有的实现"**。

手写的那版里，OAuth 部分是对的，cart/checkout 部分是错的。**同一个文件里对的和错的混在一起**，
比整块错更难发现——因为 `LoginAsync` 能工作，会让人以为整个 flow 都能工作。

---
