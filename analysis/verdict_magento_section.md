### MagentoFlow 的四个包装：两个不是 Magento

Magento 的 REST 探测（`/rest/V1/store/storeConfigs`、`/customer/section/load/`）在四个
主机上**全都没命中**。再查平台的其它标记，拿到了决定性证据：

| 主机 | `/cart.js` | 主页标记 | 结论 |
|---|---|---|---|
| `footpatrol.com` | **200** + `{"token":"d1bee53c…","note":null,"attributes":{}}` | `cdn.shopify.com` `shopify-section` `Shopify.theme` | **Shopify** |
| `size.co.uk` | **200** + `{"token":"50e1612e…"}` | 同上 | **Shopify** |
| `offspring.co.uk` | 404 | 无任何已知标记 | 都不是 |
| `jdsports.co.uk` | 404 | `__NEXT_DATA__` | **Next.js 自建** |

**`/cart.js` 返回带 token 的 Shopify cart 对象，这是铁证。**

已改：

```csharp
// 之前
public sealed class FootpatrolFlow : MagentoFlow
public sealed class SizeFlow       : MagentoFlow

// 现在
public sealed class FootpatrolFlow : ShopifyFlow
public sealed class SizeFlow       : ShopifyFlow
```

`SizeFlow` 的排队门（`PollQueueAsync`）保留了——Size? 的热门发售仍然有等待室，
URL 在排队期间会变，这和底层平台无关。

### 还有两个没改

- **`offspring.co.uk`** —— `/cart.js` 404、Magento REST 404、无任何平台标记。
  **不知道是什么，所以不动。**
- **`jdsports.co.uk`** —— `__NEXT_DATA__`，确定是 Next.js 自建。
  **但不是 Shopify，也不是 Magento，需要专门的 flow，还没写。**

`OffspringAndJdSportsAreNotMagentoEither` 把这个状态记下来了（输出它们**仍是** MagentoFlow），
而不是假装已经解决。

### 累计的平台误判

| 模块 | 原注册 | 实际 | 证据强度 |
|---|---|---|---|
| `hbx` | ShopifyFlow | 自建 `/api/v2/` | 路由自报"没有" |
| `converse` | ShopifyFlow | Demandware | `/on/demandware.store/` |
| `bstn` | ShopifyFlow | 自建 `/api/beast/` | API 前缀 + `/cart.js` 404 |
| `footpatrol` | MagentoFlow | **Shopify** | `/cart.js` token + 主题标记 |
| `size` | MagentoFlow | **Shopify** | 同上 |

**五个模块配错了平台。** 它们的共同特征：编译通过、请求返回、日志干净、业务静默失效。

### 为什么这次的证据算够

`footpatrol` / `size` 能改，是因为 `/cart.js` **返回了 Shopify 的 cart 对象**——
不是"没返回 Magento 的东西"，而是"返回了 Shopify 的东西"。

对比 `offspring`：`/cart.js` 404、Magento 404、无标记——**只知道它不是什么，
不知道它是什么**。这种不能改，改了只是把一种错换成另一种。

**"确认不是 X" 和 "确认是 Y" 是两个不同强度的结论。**

---
