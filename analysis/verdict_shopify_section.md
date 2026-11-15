### 批量验证：31 个 ShopifyFlow 包装里，25 个确认、6 个可疑

`ShopifyWrappingTests`（`Speed=Slow`）对每个 ShopifyFlow 包装的域名测 `/cart.js`——
Shopify 用 `{"token":…,"items":[…]}` 回答它，非 Shopify 不会。

```
confirmed Shopify  25
NOT Shopify         6
unreachable         6
```

**6 个可疑（`/cart.js` 不返回 Shopify 形状）**：

| 域名 | 响应 | 判断 |
|---|---|---|
| `converse.com` | 200，Nike 风格的 HTML | **最可疑**——Converse 是 Nike 旗下，用 Nike 的技术栈 |
| `civilistberlin.com` | 404，Next.js HTML | 可能是自建 |
| `bstn.com` | 404，Next.js HTML | 可能是自建 |
| `trophyroomstore.com` | 404，`{"status":404,…}` | 可能是自建 API |
| `saintalfred.com` | 200，HTML（有 `window.onload` 混淆） | 可能被拦 |
| `sns.com` | 301 重定向 | 需要跟随重定向再测 |

**6 个连不上**（`NetException`，DNS 或 TLS）：
`bodega.com` `livestock.ca` `offthehook.ca` `premiumgoodsokc.com`
`nakedcopenhagen.com` `shophmvs.com`

### 为什么不直接改这 6 个

`/cart.js` 返回 404 **不等于**不是 Shopify：

- 店铺可能挂在子路径下（`/en/cart.js`）
- 可能有地区重定向（`sns.com` 的 301）
- 可能有 WAF 拦了裸请求

改注册的前提是**确认它是什么**，不是"确认它不是什么"。
`hbx` 那个能改是因为拿到了明确否认：`"No route found for GET ...products/....json"`——
它自己说了没有那条路由，而不是"我没拿到"。

**这 6 个目前的证据只够说"可疑"，不够说"错了"。**

### 这条测试的真正价值

不是"25 个通过"，而是**把 31 个未经验证的假设变成了 25 个已验证 + 6 个待查**。

在此之前，`ShopifyFlow("converse", ...)` 和 `ShopifyFlow("bodega", ...)` 看起来一样可靠——
都是同一行代码、同样的参数形状、同样的信心。跑一次才知道它们不是一回事。

**"配置看起来对"和"配置是对的"是两件事**，只有探测能把它们分开。

---
