### 发现了一个模块配置错误（比尺码严重）

查尺码时顺手发现：**`hbx` 用的是 `ShopifyFlow`，但 HBX 不是 Shopify。**

```
new FlowStoreModule(new ShopifyFlow("hbx", "HBX", new[] { "hbx.com" }))
```

证据：

```
GET https://hbx.com/products/volley-leather-white-green.json
  HTTP 404
  {"code":404,"message":"No route found for \"GET ...products/...json\""}
```

Shopify 用 `{"product":{...}}` 回答这条路由。HBX 明确说没有。

而且 HBX 的其它特征也都不是 Shopify：

| 特征 | HBX | Shopify |
|---|---|---|
| API 前缀 | `/api/v2/` | `/products/{h}.json`、`/cart/add.js` |
| 反爬 | AWS WAF（`edge.sdk.awswaf.com`） | 无 |
| 商品路径 | `/{gender}/brands/{brand}/{product}` | `/products/{handle}` |
| 渲染 | 客户端 | 服务端 |

**用 `ShopifyFlow` 驱动它，每次加购都会打到一个返回 404 的地址。**

已换成专门的 `HbxFlow`，只写**已验证**的部分：

| 项 | 状态 |
|---|---|
| 商品路径 `/{gender}/brands/{brand}/{product}` | ✅ 已验证 |
| `GET /api/v2/shop/countries` | ✅ 已验证 |
| AWS WAF | ✅ 已验证 |
| 商品 JSON 端点 | ❌ 未知 |
| 购物车端点 | ❌ 未知 |
| 结账端点 | ❌ 未知 |

未知的三步返回**明确的原因**而不是猜一个端点：

> `"hbx: cart endpoint unknown — /products/{handle}.json is 404 and the page triggers no cart request; needs a recorded add-to-cart capture"`

猜一个 POST 打到 HBX 的 SPA catch-all 会返回 200，**看起来成功但什么都没做**——那比失败更糟。

### 尺码问题的答案：HBX 页面里没有

```
JSON keys containing 'size': (none)
商品页触发的请求：只有 /api/v2/shop/countries
页面 JSON 键：157 个，全是 i18n / 导航 / 购物车文案
```

**所以"HBX 尺码 MISS"不是解析器缺陷**，是这份数据确实不在商品页里。
`HbxFlow.FindVariantAsync` 现在明确报告"variant 端点未知"。

### 矩阵的新盲点：测"方法存在"不测"方法有效"

换成 `HbxFlow` 之后，覆盖矩阵显示 `hbx` **71%**（`+ + + + - - +`）。

但那四个 `Fail("...unknown...")` 也被计为"已实现"——**矩阵只检查方法是否 override，
不检查方法是否真的做事**。

**所以 71% 是假象。** 真实情况是 3/7 步有实现，4 步是诚实的失败。

这个盲点值得单独记为已知限制：**覆盖率的数字不能当作"能跑"的证据**，
它只说明"这段代码存在"。

### 这一轮的净收获

1. **修了一个模块配置错误**（`ShopifyFlow("hbx")` → `HbxFlow`）
2. **确认了 HBX 尺码数据不可得**（不是解析问题）
3. **发现了覆盖矩阵的新盲点**

第 1 条是实质修复，第 2、3 条是"查清了但不用改代码"。

---
