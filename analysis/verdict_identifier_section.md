### 标识符字段探针：两个 MISS 各有不同原因

`IdentifierFieldProbeTests`（`Speed=Slow`）列出商品页上所有形似标识符的字段。

**HBX —— 没有标识符字段。**

```
android    https      <- analytics 参数碎片
ID         in_ID      <- 同上
```

页面里没有任何 `productId` / `sku` / `variantId` 之类的结构化标识。HBX 的商品身份
完全由 URL 路径承载（`/{gender}/brands/{brand}/{product}`），DOM 里没有冗余副本。

**所以 `skuish` 的 MISS 不是解析器缺陷，是这类信息该站点不提供。**

**PopMart —— 字段名和流程假设不同。**

```
mainSpuID   4205, 2064, 12     <- 商品 ID，与 URL 里的 4205 一致
spuID       0                  <- 占位
skuList     null               <- 空数组字段，是干扰项
"skus":[{"id":"3220",...}]      <- 真实的 SKU 在这里
```

`PopMartFlow` 用的是 `skus[].id`（3200/3219 那种），**这是对的**。
`skuList: null` 看着像"没有 SKU"，实际真实数据在 `skus` 数组里——两个字段名只差一个
字母，语义完全不同。

**如果哪天有人图省事把 `skus` 改成 `skuList`，会静默地拿不到任何 SKU。**

### 这类探针的价值

不是"验证通过/失败"，而是**把"字段名不对"和"字段不存在"区分开**：

| 现象 | 可能原因 | 处理 |
|---|---|---|
| `skuish` MISS 但页面有 `mainSpuID` | 字段名不同 | 改正则 |
| `skuish` MISS 且页面无任何标识符 | 站点不提供 | 换身份来源（URL） |
| `skuList: null` 但 `skus` 有值 | 干扰字段 | 保持不变，别"优化" |

三种情况在只跑一次正则时看起来完全一样。

---
