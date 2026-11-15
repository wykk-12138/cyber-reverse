### BSTN 也不是 Shopify —— 自建 `/api/beast/`

```
GET  /api/beast/geoIP
POST /api/beast/monetate
GET  checkoutanalytics-live.adyen.com      <- Adyen 支付，不是 Shopify Payments
GET  /cart.js -> 404
```

`/api/beast/` 是 BSTN 自有的 API 前缀（品牌叫 **beast**inpeace）。Shopify 店铺没有这个。

已换成 `BstnFlow`，同样是"只写已验证部分"：

| 项 | 状态 |
|---|---|
| `/api/beast/` 前缀 | ✅ 已验证（geoIP、monetate 都在下面） |
| Adyen 结账 | ✅ 已验证 |
| `/us_en` 地区路径 | ✅ 已验证 |
| 商品端点 / 购物车端点 / 结账端点 | ❌ 未知 |

### 三个平台误判，三种证据形态

| 模块 | 原注册 | 实际 | 决定性证据 |
|---|---|---|---|
| `hbx` | ShopifyFlow | 自建 `/api/v2/` + AWS WAF | `404 {"code":404,"message":"No route found for .../products/....json"}` |
| `converse` | ShopifyFlow | Demandware `ConverseUS-Site` | `/on/demandware.store/Sites-ConverseUS-Site/...` |
| `bstn` | ShopifyFlow | 自建 `/api/beast/` + Adyen | `/api/beast/geoIP` + `/cart.js` 404 |

**三个都编译通过、都能跑、都返回响应。** 唯一的症状是"什么都没做成"——没有加购、
没有下单、日志干净。

这类错误的共同结构：**错误的配置比缺失的配置更难发现**，因为缺失会报错，
配错只是安静地不起作用。

### 剩下 4 个可疑还没查

`civilistberlin.com` `trophyroomstore.com` `saintalfred.com` `sns.com`

`/cart.js` 不返回 Shopify 形状，但还没拿到"自报家门"级别的证据。

**「没拿到」不同于「确认不是」**——`hbx`/`converse`/`bstn` 能改，是因为它们自己说了
自己是什么（否认某条路由、用 Demandware 路径、用自己的 API 前缀）。
这 4 个还在"可疑"阶段。

---
