### 真实页面解析验证

`ProductPageProbeTests`（`Speed=Slow`）用**模块自己的实现**跑真实商品页。

| 模块 | 状态 |
|---|---|
| `johnlewis` | 名字正确；**价格修好了**（见下） |
| `hbx` | 5/8，价格与 GA 埋点交叉一致 |
| `popmart` | 5/8，`ExtractPrice` 修好 → `39.99` |
| `casio` | 曾验证 6/8；**现在返回 2.7 KB**（限流/挑战） |

### 两个真实 bug，修法都是"宁缺毋滥"

**PopMart 的 `"price":0`**

```json
"spuPriceInfo":{"price":0,"currency":""}          // SPU 占位：未选型号时是 0
"skus":[{"id":"3220","price":3999,...}]           // SKU 真实价，单位是分
```

旧代码取第一个匹配 → `0`。修法：brace-match `"skus":[…]` → 块内扫 price → 分转美元 →
全零时退化 → **无价返回空串**（`"0"` 会被 `CheckPriceLimit` 当成免费，永远通过）。

**John Lewis 的 `£([\d.,]+)`**

页面 meta description 里有：

> "Shop the OPI range at John Lewis & Partners. Free Delivery on orders over £50."

旧正则命中这个 **"£50."** —— 一个看起来完全合理的价格，实际是包邮门槛。
而且 `ld+json` **不含 price**（只有 name 和 brand），结构化数据救不了。

修法：
1. 名字改用 `<h1>`（`<title>` 在 John Lewis 上属于页脚控件，读出来是 "Store Finder"）
2. 价格优先取站点自己标记的价格元素，其次 `og:price:amount`
3. **都没有就返回空串**

实测这个页面上确实没有标记的价格元素，所以返回 `""`——**诚实地说"不知道"，
而不是给出一个看起来合理但错的值**。

### 探针的四层"测错对象"

| 层 | 症状 | 修法 |
|---|---|---|
| 1 | 拿分类页跑商品正则，`sku` 全 MISS | 换商品页 |
| 2 | 以为列表页有商品链接 | 读渲染后的 DOM |
| 3 | 探针复制模块的正则，模块修好了探针还报旧值 | 调 `PopMartFlow.ExtractPrice` |
| 4 | **探针的正则和模块本就不同** | 调 `JohnLewisFlow.ExtractPrice` / `ExtractProductName` |

第四层最隐蔽：John Lewis 探针报 `<title>` → "Store Finder"、`price` → "50."，
**而模块压根不用这两个正则**。探针在测一个不存在的实现。

**结论**：验证工具必须调用被测对象的真实实现。四层问题全都是"测的不是那个东西"。

### 商品 URL 是怎么找到的

`NetworkRecorder.CollectLinksAsync()` 读渲染后的 DOM：

```
HBX      268 个链接  ->  /{gender}/brands/{brand}/{product}
PopMart  186 个链接  ->  /us/products/{id}/{slug}
```

**John Lewis 的 DOM 里没有商品链接**（首页 87 个、搜索页 137 个，全是导航），
URL 格式 `/{brand-product}/{variant}/p{id}` 是从外部搜索确认的。

上一版用了一个**编造的 p 号**，404 来自那个号码而不是路径模式。
**"格式对但 id 假"和"格式错"看起来一模一样**，这个区别差点让我否掉正确的假设。

### 仍然拿不到的 4 个

```
warhammer      202 + 2 KB challenge page, technology not identified
supreme        403
scheels        403, Kasada (same build as Nike)
yeezysupply    site retired
```

### 一条反复应验的规律

拿不到数据时，先问「**这份输入里到底有没有我要的东西**」，再决定是换输入还是改解析。
四次踩坑三次属于这个：

1. 分类页跑商品正则 → 数据不在
2. 列表页找商品链接 → 数据不在（JS 渲染）
3. 编造 p 号 → 路径对但实体不存在

第四次（探针正则和模块不同）属于另一类：**输入对了，但在测别的东西**。

---
