### Offspring 是 SAP Commerce (Hybris) —— 第八个平台误判

`OffspringFlow` 一直继承 `MagentoFlow`，但**没有任何 Magento 接口应答过**：
`/rest/V1/store/storeConfigs` 404、`/customer/section/load/` 404、`/cart.js` 404。

抓首页看到它实际调的是：

```
GET  /akam/13/710368ee                          Akamai Bot Manager
GET  /view/resources/getUserInfo                -> 200, 418B,  application/json
GET  /view/component/basket/minibasketAjax      -> 200, 1164B, application/json
```

**页面 HTML 里字面包含 `hybris`。** `/view/...` 是 SAP Commerce 的 controller 形状——
不是 Magento，不是 Shopify，不是 Demandware。

**这是 A 级证据**：站点自己说出了后端名字，而且两个 controller 返回真实 JSON。

### 新增 `HybrisFlow`

`src/Cybersole.Stores/Flows/HybrisFlow.cs`，平台数 **14 → 15**。

| 步骤 | 依据 |
|---|---|
| `GetHomeAsync` | ✅ 验证（顺带调 `getUserInfo` 确认会话可用） |
| `GetCartAsync` | ✅ 验证（`minibasketAjax` 返回 JSON） |
| `FindProductAsync` | 按 Hybris 形状（`<h1>` 名称 + `"code"` 变体） |
| `FindVariantAsync` | 同上 |
| `AddToCartAsync` | ⚠️ 推测（`POST /cart/add` + `productCodePost`/`qty`） |
| `SubmitOrderAsync` | ❌ Hybris 是分阶段 controller 流（配送 → 支付 → 复核），没有单一提交 |

加购 404 时的话是：

> `"offspring: /cart/add not found — the Hybris controller path is inferred from the
> documented shape; only the two read-only /view/ controllers are verified"`

——**说清哪些验过、哪些没验过**，不推给网络。

### 八个平台误判

| 模块 | 原注册 | 实际 |
|---|---|---|
| `hbx` | ShopifyFlow | 自建 `/api/v2/` |
| `converse` | ShopifyFlow | Demandware |
| `bstn` | ShopifyFlow | 自建 `/api/beast/` |
| `footpatrol` | MagentoFlow | Shopify |
| `size` | MagentoFlow | Shopify |
| `funko` | site id `Funko-Site` | `FunkoUS-Site` |
| `jbhifi` | 手写 StoreFlow | Shopify + 独立 OAuth |
| **`offspring`** | **MagentoFlow** | **SAP Commerce (Hybris)** |

**这是最后一次"可能配错平台"的模块。** 剩下的都有定性结论。

### 平台覆盖 15 / 15

`Shopify` `Magento` `Demandware` `Footsites` `Supreme` `Kasada` `Nike` `Queue-it`
`Goat` `Scheels` `Hbx` `Bstn` `PopMart` `Swell` **`Hybris`**

---
