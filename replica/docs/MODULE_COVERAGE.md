# MODULE_COVERAGE — 每个 Flow 实现了哪些必需步骤

表格里的 + 表示该 Flow 有自己的实现，- 表示仍走基类的拒绝。
表格里的 `+` 表示该 Flow 有自己的实现，`-` 表示仍走基类的拒绝。

**这一节回答的是 R24 暴露的盲点**：`impl_quality.py` 只把 `=> Ok();` 算缺口，
后者不是空实现，是未实现，比空实现更糟。

| Flow | FindProduct | FindVariant | AddToCart | GetCheckout | SubmitShipping | SubmitPayment | SubmitOrder | 完成度 |
|---|「 + 「---|「 * len(REQUIRED) + 「---|
| `FootsitesFlow` | + | + | + | - | + | + | + | 86% |
| `SupremeFlow` | + | + | + | + | + | - | + | 86% |
| `MagentoFlow` | + | + | + | - | + | + | + | 86% |
| `JohnLewisFlow` | + | + | + | - | + | + | + | 86% |
| `NikeFlow` | + | + | + | - | - | - | + | 57% |
| `PopMartFlow` | + | + | + | - | - | - | + | 57% |
| `YeezySupplyFlow` | + | + | + | - | - | - | + | 57% |
| `CasioFlow` | + | + | + | - | - | - | + | 57% |
| `WarhammerFlow` | + | + | + | - | - | - | + | 57% |
| `JbHiFiFlow` | + | + | + | - | - | - | + | 57% |
| `SuperswipeFlow` | + | + | + | - | - | - | + | 57% |
| `PocketGamesFlow` | + | + | - | - | - | - | - | 29% |
| `HypeCommerceFlow` | + | + | + | - | - | - | + | 57% |
| `FanaticsFlow` | + | + | + | - | - | - | + | 57% |
| `RiotGamesFlow` | + | + | - | - | - | - | - | 29% |
| `RaffleFlow` | - | - | - | - | - | - | - | 0% |
| `ShopifyFlow` | + | + | + | + | + | + | + | 100% |

## 汇总

- Flow 总数：**17**
- 7 个必需步骤全覆盖：**1**（6%）

| 步骤 | 实现它的 Flow 数 |
|---|---|
| `FindProduct` | 16 / 17 |
| `FindVariant` | 16 / 17 |
| `AddToCart` | 14 / 17 |
| `GetCheckout` | 2 / 17 |
| `SubmitShipping` | 5 / 17 |
| `SubmitPayment` | 4 / 17 |
| `SubmitOrder` | 14 / 17 |

## 怎么读这张表

不是每个 Flow 都该实现全部 7 步。`RiotGamesFlow` 是抽签制，没有 `SubmitShipping`；
`RaffleFlow` 没有 `SubmitPayment`。**缺口分两种**：

1. **业务上不需要** —— 抽签站、预约站天然没有结账链。这类不算缺口。
2. **该做而未做** —— 一个正常电商 Flow 缺 `FindVariant`，那就是真缺口。

这张表只回答「有没有「，「该不该有「要逐个看业务。
