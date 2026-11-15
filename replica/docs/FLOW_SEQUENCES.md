# 六条流的序号缺口：找到了一条**能走的**路（R269）

## 一、结论先写

镜像里有 **69 段字面量**，每一段同时包含：

- 一个 `d__` 状态机连续段（**方法名 + 编译器序号**，按声明顺序）；
- 同一批方法的 `b__N_M` lambda 表（**序号与方法名再次出现**）。

两者**在同一段字面量里互相印证序号**，所以段内顺序可信。合并去重后共恢复
**320 个"方法 + 序号"配对**。

```
python analysis/flow_dump.py   →   flow_step_sequences.json
```

## 二、为什么这解决了 R268 说"不成立"的那件事

R268 量化过：**同一个序号平均挂 5.58 个不同方法** —— 因为序号是**每个类各自编号**，
所以"全库按序号归堆"必然错。

但**段内**不同：一段字面量属于**一个类**，段里的序号序列就是那个类的方法声明顺序。
R121 用这个方法解开了 John Lewis（17 步，序号 20→23 的缺口）。

**区别在于"归堆的范围"**：全库归堆无效，段内归堆有效。

## 三、样例（真实输出）

| 地址 | 段内序号→方法 |
|---|---|
| `0x03385140` | `8:Login, 9:FindProduct, 10:AddToCart, 11:GetCheckout, 12:SubmitShipping, 13:SubmitRate` |
| `0x0336dea7` | `33:GetCsrf, 34:GetCheckout, 35:GetCheckoutHtml, 36:AddToCart, 37:AddToCart2, 38:SubmitDiscount, 39:SubmitShipping, 40:SubmitOrder` |
| `0x03396fa0` | `4:AddToCartStoreFront, 5:RefreshSession` |

第 2 行正是一条**完整的结账流水线**：取 CSRF → 取结账页 → 加车 → 折扣 → 运费 → 下单。

## 四、还缺一步：把段绑定到**商店**

段本身不带类名。可选办法（按可靠性排序）：

1. **段首地址附近的其他字面量**：有些相邻行就是 `<>c__DisplayClassN_M`，仍不带类名；
2. **方法名指纹**：不同商店的方法名组合有特征（`Popmart` 有 `GetLotteryForm`、`Nike` 有 `Get6Js`）；
3. **与已知流对照**：John Lewis 已解开，可用它的段做锚点，看相邻地址段的命名风格。

**这三条都还没做** —— 下一轮从这里开始。

## 五、给复刻件的用法

`StoreFlowSteps` 现在钉住六条流的步数。用这份 320 条配对，可以：

- **核对**已有六条流的步表（段内序号连续则步表不该有缺口）；
- **扩充**其它商店的步表（每条流 8–20 步，320 条足够覆盖十几家）。

**注意**：段内序号连续并不等于"步骤连续"——`d__N` 里既有步骤也有助手方法（Nike 的 45/47 就是助手）。
所以扩充时要按 R119 的规则：**缺口用该段的 lambda 表判**，不是一律当步骤。

## 六、把段绑定到商店：三条路，两条走通一半、一条死

### 1. 方法名指纹（**9 / 69** 段绑上，且看起来是对的）

用"独有名词"（`Get6Js`/`FetchSensor`→Nike、`GetLotteryForm`/`CheckRaffleStatus`→Popmart、
`AddToCartStoreFront`/`SubmitDiscount`→Shopify、`DeleteBasket`/`SubmitBilling`→Demandware），
**只有 9 段命中**，但命中都很像真的：

| 地址 | 指纹 | 全段 |
|---|---|---|
| `0x03390d79` | Shopify | `26:FindProduct, 28:AddToCart, 29:SubmitDiscount, 30:GetCheckout, 31:GetShippingRates, 33:GetPaypalId, 34:GetPaypalBearer, 35:ProcessPaymentPaypalCreditCard, 37:ProcessOrderPaypalCreditCard, 38:SubmitOrder, 39:ProcessOrder` |
| `0x0336dea7` | Shopify | `33:GetCsrf … 38:SubmitDiscount, 39:SubmitShipping, 40:SubmitOrder` |
| `0x0338a27a` | Demandware | `12:GetShippingRates, 13:SubmitShipping, 14:SubmitBilling, 15:SubmitOrder` |

用**通用**名词（`GetCsrf`/`SubmitOrder`/`SubmitShipping`）会命中 27 段，但那些名字几乎每家都有 → **不可用**。

### 2. 段邻近字面量里找商店名：**0 / 69**

**死路。** 段附近从没出现过商店名 —— 类名不在字面量池的这一带。

### 3. 用已解开的 John Lewis 段当锚点：未做

## 七、两个数据质量警告（这一轮才发现的）

1. **段内序号并不连续**：`0x03398963` 是 `5:CheckRaffleStatus, 68:GenerateVariables`。
   所以"连续段"其实是**同一个类的方法在元数据里的顺序**，中间可以跳号；
   拿它当"步骤表"时**不能按序号连续性推步骤**。
2. **序号可能是解析产物**：`0x03380d89` 里出现 `356:SubmitPayment` —— 明显是相邻数字粘连。
   **凡序号 > 200 的一律复核**再入库。

## 八、又两条路被排除（R271）

### 1. 段内**方法名里从不出现商店名**（0 / 69）

扫了 20 个商店名（Nike / Popmart / Shopify / Footlocker / Demandware / Magento / Goat / Scheels /
HBX / Casio / Farfetch / Warhammer / Supreme / Adidas / Yeezy / Snkrs / Amazon / Target / Walmart），
**任何一段的方法名里都没有它们** —— 方法名是纯动作名（`AddToCart`、`SubmitOrder`），不带品牌。

### 2. 想用"复刻件自己的商店模块"生成指纹 —— 也走不通

复刻件的商店模块**不是一个模块一个文件**（`src/Cybersole.Http/Stores/` 下只有一个
`Stores.Abstractions.cs`，模块是数据驱动的），所以"每个模块的独有方法"这个思路没有对象可切。

### 3. 一个有用的统计

```
段内方法名总数 216    只出现在一段里的 172（80%）
```

**80% 的方法是"某一段独有"的** —— 这意味着指纹法**理论上限很高**，
真正的瓶颈不是"名字不够独特"，而是**我不知道哪个独特名字属于哪家店**。

## 九、所以段→商店这条线的真实边界

| 路 | 结果 |
|---|---|
| 通用动作名指纹 | 27 段命中但不可判 |
| 独有动作名指纹（人工列的 4 组） | 9 段绑上 |
| 方法名含商店名 | **0** |
| 段邻近字面量含商店名 | **0** |
| 复刻件模块独有方法 | 无对象可切 |
| John Lewis 锚点 | 未做（唯一剩下的路） |

**结论**：段→商店**只能靠外部知识**（我知道 `Get6Js` 是 Nike 的、`GetLotteryForm` 是 Popmart 的），
镜像是**不会自己说的**。这条线到此为止，除非用 John Lewis 段把锚点扩出来。

## 十、**关键进展**：镜像里有两种布局，第二种把 John Lewis 完整解出来了（R272）

### 1. 两种布局

| 布局 | 形态 | 例子 |
|---|---|---|
| **A 合并式** | 一行里塞一批 `d__N` + lambda 表 | 69 段 / 320 配对（R269） |
| **B 分行式** | **每个 `d__N` 各占一行**，行地址间隔 ~0x30 | John Lewis、以及另外 38 段 |

上一轮我按 A 的形态去找 John Lewis，找不到 —— 因为它用的是 B。

### 2. B 的判据（可复算）

> 连续若干行，**每行内容恰好是 `<方法名>d__序号`**（行首可能有一个长度字节的残留字符），
> 且**行地址间隔 ≤ 0x60**；凑够 3 行以上即为一段。

`tools/row_groups.py` → `docs/row_groups.json`（39 段 / 159 步）。

### 3. 解出来的 John Lewis（0x3371cea，16 步）

```
22:Start 24:GetHome 25:FindProduct 26:GetProductHtml 27:FindVariant
28:AddToCartPreload 29:EditLine 30:SubmitEmail 31:GetShippingRate 32:SubmitShipping
33:SubmitBilling 34:SubmitOrder 35:CompleteOrder 36:GetCartCsrf 37:GetPayPalOrderId
```

**与 R112 读到的 17 步表对比**：缺 `23`（R112 也发现 20 跳到 23），且这里多了
`31:GetShippingRate / 32:SubmitShipping / 33:SubmitBilling / 34:SubmitOrder / 35:CompleteOrder` ——
**这正是 R112 当年没读到的那几步**，现在从镜像里直接读出来了。

### 4. 意义

B 布局的段**不需要 lambda 互证**，判据简单（相邻行 + 命名形态），所以可以用它把**所有**这类类都解出来。
39 段 / 159 步只是起点 —— 提高"地址间隔"与"最少行数"的容忍度还可以扩。

## 十一、把两种布局合起来清点：**18 条流水线 / 141 步**（R273）

### 1. 布局 B 会混进非商店类

放宽判据（≥2 行、间隔 ≤0xC0）后 B 有 **129 段 / 380 步**，但里面混着编辑器的 `Copy/Cut/Paste`、
连接的 `ConnectionLoop`、传感器的 `GenerateSensor` —— **B 抓的是"所有异步类"，不是"所有商店流程"**。

### 2. 用"结账词汇"过滤

一段里若出现 ≥2 个结账动作名（`AddToCart`/`FindProduct`/`GetCheckout`/`SubmitOrder`/`SubmitShipping`/
`SubmitBilling`/`GetCartCsrf`/`SubmitDiscount`/`EnterRaffle` …）才算流水线：

```
布局 A 69 段 -> 流水线 15 段
布局 B 129 段 -> 流水线 3 段
合并去重         -> 18 条流水线 / 141 步
```

### 3. 最长的几条（真实输出）

| 段基址 | 步数 | 开头 |
|---|---|---|
| `0x034b14b8` | 15 | `FindProductMulti, FindProductFlow, FindVariant, AddToCartMulti, GetCheckout, GetMerchantCode …` |
| `0x3371cea` | 15 | `Start, GetHome, FindProduct, GetProductHtml, FindVariant, AddToCartPreload …`（**John Lewis**） |
| `0x034b23a5` | 12 | `EditLine, AddToCart, GetCheckout, GetShippingRate, SubmitShipping, CalculateTaxes …` |
| `0x03390d79` | 11 | `FindProduct, AddToCart, SubmitDiscount, GetCheckout, GetShippingRates, GetPaypalId …`（Shopify） |
| `0x033895e0` | 11 | `GetCsrf, GetCheckout, ApplyDiscount, GetShippingRates, SubmitShippingInformation, SubmitPaymentDetails …` |
| `0x337fa33` | 10 | `GetCart, ClearCart, FindProduct, AddToCart, ReplaceProduct, GetCsrf …` |

### 4. 与复刻件的关系

复刻件的 `StoreFlowSteps` 目前只钉住六条流。这里的 18 条是**可以逐条核对/扩充的上限**，
但每条的**商店归属**仍然只解出 9 条（独有指纹），其余 9 条只能按"步骤形状"归档。

> 注意：`0x3371cea` 只有 15 步（含 `Start`），而正文里写的 John Lewis 是 16 步 —— 差的一步是
> `21`/`23` 那种**跳号**造成的。**段内序号不连续，别拿"步数"当"序号差"。**

## 十二、拿复刻件的 `StoreFlowSteps` 对账：**它其实有两类行**（R274）

用 18 条恢复出来的段去对 `src/Cybersole.Stores/Flows/StoreFlowSteps.cs` 里的 8 条流：

| 流 | 步数 | 命中 | 最佳段 |
|---|---|---|---|
| **structure-token-multi** | 15 | **15 / 15** | `0x034b14b8` |
| **structure-token-single** | 12 | **11 / 12** | `0x034b23a5`（缺 `GetMerchantCode`） |
| johnlewis | 19 | 4 / 19 | `0x3371cea` |
| nike | 16 | 2 / 16 | `0x3371cea` |
| demandware-classic | 12 | 3 / 12 | `0x034b23a5` |
| demandware-dual | 15 | 2 / 15 | `0x03390d79` |
| popmart | 24 | 0 / 24 | — |
| collectplus-app | 17 | 3 / 17 | `0x3378cb1` |

### 两类行，证据强度完全不同

| 类 | 例子 | 命中率 | 说明 |
|---|---|---|---|
| **字面量派生** | `structure-token-multi` / `-single` | **15/15、11/12** | 直接读自一段字面量 → **被这次恢复完全证实** |
| **端点派生** | nike / popmart / johnlewis / demandware / collectplus | 0–4 | 当年是**按端点族"讲出来"的**，名字与字面量里的方法名不是同一套 |

例如复刻件写 `StartEcomSession`，字面量里是 `Start`；写 `SubmitConsignment`，字面量里是 `SubmitShipping`。
**这不是错，是两种不同的东西**：一类是"镜像里的步骤表"，一类是"我们据端点推断的行为模型"。

### 结论（写进对账纪律）

> **`StoreFlowSteps` 里的行必须标清来源**：`literal`（可直接对账）还是 `endpoint`（叙述性，不可与字面量逐条比对）。
> 不标来源的"1:1"，是把两种证据混在一起算。

## 十三、用"复刻件当字典"去找归属：只确认了已知两条（R276）

思路：拿 18 条流水线的步骤名，去复刻件源码里数命中，看命中最多的是哪个文件。

| 段 | 步数 | 命中最多 |
|---|---|---|
| `0x034b14b8` | 15 | **`StoreFlowSteps.cs` 15 / 15** ← 已知的 structure-token-multi |
| `0x034b23a5` | 12 | **`StoreFlowSteps.cs` 12 / 12** ← structure-token-single |
| `0x03388fd2` | 8 | `StoreFlowSteps.cs` 8（**待复核**，见下） |
| `0x3371cea` | 15 | `StoreFlowSteps.cs` 9 / `StoreFlowRunner.cs` 8 |
| 其余 14 条 | — | 命中最多的是 **`StoreFlowRunner.cs`** —— 那是**通用步骤执行器**，里面本来就有一堆通用动作名 |

**结论**：这条路线只确认了已知的两条；其余 14 条命中的是通用执行器的词汇，**不构成归属证据**。

### 待复核项 **已复核完毕**（R277）

`0x03388fd2` 之前没在 `row_groups_wide.json` 里找到 —— 因为它是 **A 布局**的段（在
`flow_step_sequences.json` 里），不是 B 布局。内容：

```
11:FindProductFlow  12:GetCheckout  13:GetShippingRate  140:SubmitShipping
150:GetStructureToken  16:CreateTransaction  17:SubmitPayment  18:ProcessPayment
```

命中情况：`structure-token-multi` **8/15**、`structure-token-single` **7/12** ——
**它是 structure-token 家族的第三个片段（子集）**，和那两条共享 `CreateTransaction` /
`GetStructureToken` / `ProcessPayment` 等词汇。所以"两边都命中"不是矛盾，是**同族**。

（顺带印证了 R270 的警告：`140` / `150` 这种大序号是**数字粘连的解析产物**，不是真序号。）

### 所以"再找可标 Literal 的流"这条待办 → **关闭（否证）**

恢复集里的 18 条，除已知两条外都与复刻件的命名体系不重合 ——
说明它们属于**复刻件还没建模的商店**，而不是"标错来源"。
