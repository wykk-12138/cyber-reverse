### 平台误判表也有锚点了

上轮锚住了模块数和错误文案数。这轮锚的是**最值钱的那张表**——
`PLATFORM_VERIFICATION.md` 第一节的"已知误判"。

它已经漂了：

- 标题写「五个已知误判」，表里 **7 行**
- `jbhifi`（第八个）**完全不在表里**

### 修完后的表（按发现顺序）

| 模块 | 原注册 | 实际 |
|---|---|---|
| `hbx` | `ShopifyFlow` | `HbxFlow`（自建 `/api/v2/`） |
| `converse` | `ShopifyFlow` | `DemandwareFlow` |
| `bstn` | `ShopifyFlow` | `BstnFlow`（自建 `/api/beast/`） |
| `footpatrol` | `MagentoFlow` | `FootpatrolFlow : ShopifyFlow` |
| `size` | `MagentoFlow` | `SizeFlow : ShopifyFlow` |
| `funko` | `DemandwareFlow("Funko-Site")` | `FunkoFlow`（`FunkoUS-Site`） |
| `jbhifi` | `StoreFlow`（`/api/cart/add`） | `JbHiFiFlow : ShopifyFlow` |
| `offspring` | `MagentoFlow` | `HybrisFlow` |

### 新增 `PlatformTableTests`（2 个测试）

**一、标题数字 == 表格行数**

把中文数字（五/六/七/八…）和阿拉伯数字都转成整数比对：

```
heading claims: 8
table rows:     8
modules:        hbx, converse, bstn, footpatrol, size, funko, jbhifi, offspring
```

**二、没有任何一行仍然解析成表里说错的那个 flow**

```
hbx            was ShopifyFlow        now HbxFlow
converse       was ShopifyFlow        now DemandwareFlow
bstn           was ShopifyFlow        now BstnFlow
footpatrol     was MagentoFlow        now FootpatrolFlow
size           was MagentoFlow        now SizeFlow
funko          was DemandwareFlow     now FunkoFlow
jbhifi         was StoreFlow          now JbHiFiFlow
offspring      was MagentoFlow        now HybrisFlow
```

**`funko` 是例外**：它的类型没变（还是 `DemandwareFlow` 的子类），错的只是 site id。
所以对它断言 `IsAssignableFrom<DemandwareFlow>`，而 site id 由
`PlatformAssignmentTests.FunkoUsesTheRealDemandwareSiteId` 单独钉住。

### 第一次写这个测试时我犯了什么错

第一版断言的是「表格『实际』列里的类名 == registry 的类名」。

跑出来才发现：**那一列写的是平台名（`**Shopify**`、`自建 /api/v2/`），不是类名。**

```
hbx            table says 自建 `/api/v2/` + AWS WAF     registry says HbxFlow
footpatrol     table says **Shopify**                   registry says FootpatrolFlow
```

**我按自己的想象设计了断言的形状，而不是先看表格里到底写了什么。**

改成「原注册列提到的类 ≠ 当前类」之后才对——因为那张表的语义是
**"以前是 X，现在不是 X"**，不是"现在是什么"。

### 现在的锚点总表

| 文档 | 断言 | 类型 |
|---|---|---|
| VERDICT | 61 个模块 | 事实 |
| VERDICT | 13 条错误文案 | 事实 |
| VERDICT | p50 必须标注样本数 | 测量 |
| VERDICT | Settings 页数必须标注"基线" | 快照 |
| PLATFORM_VERIFICATION | 标题数字 == 行数 | 事实 |
| PLATFORM_VERIFICATION | 每行都已修正 | 事实 |

**六条锚点，全部在 `dotnet test` 里跑。**

---
