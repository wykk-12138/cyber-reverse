### Supreme 也是 Shopify —— 第九个平台误判

上轮说「验 `supreme`，它 86%，差在哪值得看一眼」。查下来**差的不是一步，是整套前提**。

### 抓包发现 `shopifysvc`

```
18  us.supreme.com
5   otlp-http-production.shopifysvc.com     ← Shopify 的遥测服务
 /shop/all  ->  308  ->  us.supreme.com/collections/all
```

`/collections/` 是 Shopify 的标准路径。然后决定性的一条：

```
GET https://us.supreme.com/cart.js
-> 200, text/javascript, 303 B

{"token":"1ebefd3e73c2f4f214e9f5865af289c0","note":null,"attributes":{},
 "original_total_price":0,"total_price":0,"total_discount":0,"total_weight":0.0,…}
```

**Shopify cart 对象。**

### 原来那 193 行是什么

```csharp
/// Supreme — form-post checkout, no JSON API. The whole flow is: product page →
/// colour id → /shop/{id}/add → /checkout POST with a form body.
```

**产品页拿 CSRF、颜色 id、POST `/shop/{id}/add`、表单 POST 到 `/checkout`。**

**这些全都不存在了。** 不是"差一步"，是**整套自定义流程被换成了 Shopify**。

### 改法

200 行 → 36 行：

```csharp
public sealed class SupremeFlow : ShopifyFlow
{
    public SupremeFlow() : base("supreme", "Supreme", new[]
    {
        "us.supreme.com",        // 真正的店面
        "supreme.com",           // 重定向到它
        "supremenewyork.com",    // 旧域名，也重定向
    })
    {
    }
}
```

覆盖矩阵 **86% → 100%**，`fully covered` 从 46 回到 **46**（`supreme` 补上，其他不变）。

### 一个重要的观察

**86% 那个数字在骗人。**

`SubmitPayment` 那一格是 `-`，看起来"只差一步"。实际上：

- 那 6 个 `+` 的步骤**全都是错的**（打向不存在的端点）
- 唯一"缺"的那一步**根本不需要**（Shopify 支付在下单里）

**覆盖率衡量的是"有没有实现"，不是"实现对不对"。**

86% 的模块比 71% 的模块更糟——因为 71% 的那些至少诚实地 `Fail` 了。

### 九个平台误判

| 模块 | 原注册 | 实际 |
|---|---|---|
| `hbx` | ShopifyFlow | 自建 `/api/v2/` |
| `converse` | ShopifyFlow | Demandware |
| `bstn` | ShopifyFlow | 自建 `/api/beast/` |
| `footpatrol` | MagentoFlow | Shopify |
| `size` | MagentoFlow | Shopify |
| `funko` | site id `Funko-Site` | `FunkoUS-Site` |
| `jbhifi` | 手写 StoreFlow | Shopify + 独立 OAuth |
| `offspring` | MagentoFlow | Hybris |
| **`supreme`** | **手写 193 行** | **Shopify** |

**九个，全部有 live contract 守着。**

### 怎么发现这个的

不是因为怀疑 `supreme`，是因为**它 86% 很扎眼**——61 个模块里只有它一个是 86%。

**反常的数字值得看一眼，哪怕它的绝对值看着不错。**

---
