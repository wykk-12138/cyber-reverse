### Converse 也不是 Shopify —— 是 Demandware

`converse.com` 在上一轮的 `/cart.js` 探测里可疑（返回 Nike 风格 HTML）。抓一次真站点，
证据很硬：

```
/on/demandware.store/Sites-ConverseUS-Site/default/Cms-GetProductStrip?cgid=new-arrivals
/on/demandware.static/Sites-ConverseUS-Site/-/default/v1794294607470/images/loading.gif
/on/demandware.store/Sites-ConverseUS-Site/default/Promotion-PromotionCountdownModule

x-queueit-ajaxpageurl: https%3A%2F%2Fwww.converse.com%2F
x-kpsdk-v=j-1.2.988
```

`/on/demandware.store/Sites-{SiteId}/` 是 Demandware（Salesforce Commerce Cloud）独有路径，
site id 就是 `ConverseUS-Site`。

顺带两个发现：

- **Converse 也用 Kasada**（`j-1.2.988`，和 Nike / Scheels 同一构建号）
- **还有 Queue-it 排队**（`x-queueit-ajaxpageurl`），这是 Nike 系站点的典型配置

已换成：

```csharp
new FlowStoreModule(new DemandwareFlow("converse", "Converse",
    new[] { "converse.com" }, "ConverseUS-Site")),
```

覆盖矩阵从"Shopify 100%（假）"变成"Demandware 100%（真）"。

### 两个平台误判的共同点

| 模块 | 原来 | 实际 | 决定性证据 |
|---|---|---|---|
| `hbx` | `ShopifyFlow` | 自建 `/api/v2/` + AWS WAF | `404 {"code":404,"message":"No route found for ...products/....json"}` |
| `converse` | `ShopifyFlow` | Demandware `ConverseUS-Site` | `/on/demandware.store/Sites-ConverseUS-Site/...` |

**两个都编译通过、都能跑、都返回响应。** 唯一的症状是"什么都没做成"。

`PlatformAssignmentTests` 把这四个赋值钉住了：

```
hbx       必须是 HbxFlow，不能是 ShopifyFlow
converse  必须是 DemandwareFlow，且 SiteId == "ConverseUS-Site"
bodega / kith / undefeated / bstn   必须是 Shopify 系
所有模块必须有域名
```

（最后一条是防回归：空域名会让 `CatalogValidatorTests` 报
`module 'x' declares no domains`，这里提前拦住。）

### 剩下 5 个可疑还没查

`civilistberlin.com` `bstn.com` `trophyroomstore.com` `saintalfred.com` `sns.com`
——`/cart.js` 不返回 Shopify 形状，但也没拿到"明确否认"。

**"没拿到"不同于"确认不是"。** `hbx` 和 `converse` 能改是因为它们自己说了自己是什么
（一个说"没有这条路由"，一个用 `/on/demandware.store/` 自报家门）。
这 5 个还没到那一步。

---
