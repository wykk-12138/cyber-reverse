# 端点证据账（R293）

复刻件 `src/` 里的 API 路径，逐条对照镜像字符串池的结论。重算：`tools/endpoint-ledger.py`。

## 总数

| 桶 | 条数 | 含义 |
|---|---|---|
| **逐字命中** | **44** | 路径在池子里原样存在 |
| **由片段组成** | **23** | 整条没有，但它的尾段在池子里（如 `/cart/add`）—— 属于组合，不是自造 |
| **无证据** | **22** | 整条和尾段都找不到 |

```
复刻件 API 路径 89  =  44 逐字 + 23 组合 + 22 无证据
```

## 无证据的 22 条（`EndpointEvidenceRatchetTests` 盯着）

| 路径 | 使用处 |
|---|---|
| `/account/recover` | `Flows/StoreFlow.cs` |
| `/account/verify` | `Flows/MagentoFlow.cs` |
| `/api/basket/v1/items` | `Flows/FarfetchFlow.cs` |
| `/api/beast` | `Flows/BstnFlow.cs` |
| `/api/checkout/submit` | `Flows/RetailFlows.cs` |
| `/api/checkout/v1/basket/{basketId}` | `Flows/FarfetchFlow.cs` |
| `/api/checkout/v1/basket/{basketId}/place-order` | `Flows/FarfetchFlow.cs` |
| `/api/checkout/v1/basket/{basketId}/shipping` | `Flows/FarfetchFlow.cs` |
| `/api/order/submit` | `Flows/PopMartEndpoints.cs` |
| `/api/preorder/entry` | `Flows/RetailFlows.cs` |
| `/api/search` | `Flows/ScheelsFlow.cs` |
| `/api/stock` | `Flows/PopMartEndpoints.cs` |
| `/api/v1/carts/{c.Session.CartId}` | `Flows/HbxFlow.cs` |
| `/api/v1/carts/{c.Session.CartId}/items` | `Flows/HbxFlow.cs` |
| `/api/v2/shop/countries` | `Flows/HbxFlow.cs` |
| `/collections/new-releases` | `Flows/MagentoFlow.cs` |
| `/rest/V1/carts/mine/totals` | `Flows/MagentoFlow.cs` |
| `/v1/buys` | `Flows/GoatFlow.cs` |
| `/v1/buys/{c.Session.CartId}` | `Flows/GoatFlow.cs` |
| `/view/resources/getUserInfo` | `Flows/HybrisFlow.cs` |
| `/v1/carts/{c.Session.CartId}/items` | `Flows/HbxFlow.cs` |

## 这 22 条怎么处理（按优先级）

1. **先找证据**：有些可能以别的形态存在（拼接、模板、变量前缀），值得再查一轮；
2. **找不到就标"推断"**：在源码注释里写明"无镜像证据"，不冒充 1:1；
3. **不删**：它们是可用逻辑，删掉会让对应商店流程退化；账本负责让它们**可见**，而不是让它们消失。

## 口径说明（重要）

- "逐字命中"= 整条字符串在池子里；
- "由片段组成"= 尾 1–2 段能在池子里找到 —— 这是**弱证据**，只证明"名字不假"，不证明整条路径对；
- 池子里还有 218 条 API 形状路径，其中多数（`/Assets/*`、挑战 URL、3DS 回调）不属于本账范围。

---

## R294：再找一轮证据 + 在源码里标「推断」

### 1. 换匹配方式又找到 3 条

上一轮只做"整条路径在池子里"，这一轮加了两条更宽的判据（**URL 里包含该路径**、**去掉模板占位符按前缀查**）：

```
/api/v1/carts/{c.Session.CartId}         <- https://hbx.com/api/v1/carts
/api/v1/carts/{c.Session.CartId}/items   <- https://hbx.com/api/v1/carts
/v1/carts/{c.Session.CartId}/items       <- api/v1/carts
```

→ 无证据从 **22 → 18**（HBX 的三条其实是同一族，账本按路径去重后减 3）。

### 2. 剩下 18 条：在源码里逐条标 `inferred: no image evidence (R294)`

标记落在**使用该路径的代码行**上（不是文档注释），共 19 处标记覆盖 18 条路径（HBX 三条共用两行）。

于是读那段流程代码的人，**不会把推断当成证据**。

### 3. 棘轮升级

`EndpointEvidenceRatchetTests` 新增第三条：**每个用无证据路径的文件里必须出现这句标记**。
少了任何一处，测试就红。

## R294 的诚实结论

| 判定 | 条数 |
|---|---|
| 逐字命中 | 44 |
| 片段组成（弱证据） | 23 |
| **URL 包含 / 前缀命中** | **3** |
| **仍无证据（已标推断）** | **18** |

**这 18 条没有被删除，也没有被当成证据** —— 它们现在是"已知的推断"，而不是"看起来像证据的东西"。

---

## R296：请求头也查了一遍 —— 16 个里 13 有证据，1 个改了名，2 个是内部诊断

用同样的方法查复刻件里的**头名字面量**（16 个）：

| 结果 | 数量 | 说明 |
|---|---|---|
| 池子里逐字命中 | **13** | 直接用 |
| 内部诊断（**不是发出去的**） | 2 | `X-Cyb-Transport` / `X-Cyb-Alpn` —— 写在 `result.Headers[...]` 上，是**响应侧记录**"这条请求走了哪条 TLS/ALPN"，不进请求 |
| 改名的 | 1 | `X-CSRF-Token` |

### 那一处改名（真缺陷，已改）

- 复刻件原来发 `X-CSRF-Token`；
- 池子里**没有**这个拼写，只有小写 `x-xsrf-token`；
- 已把 `StoreFlow.cs` 里发送的名字改成 **`x-xsrf-token`**（两处），
  `GoatFlow.cs` 的文档注释也从 "X-CSRF-TOKEN" 对齐到同一拼写。

> GOAT 的 cookie 名仍是 `XSRF-TOKEN`（那是 **cookie**，不是请求头），保持不变。

### 教训

`X-Cyb-*` 那两个名字看着吓人（像是自己编的、会暴露指纹），查了才发现**它们挂在响应对象上**，
根本不发出去。**"头形状的字符串" ≠ "请求头"** —— 判方向比判存在更重要。

---

## R297：cookie 名也查了 —— 5 个里 2 个有证据，3 个已标推断

| cookie 名 | 证据 | 使用方式 |
|---|---|---|
| 2 个 | 池子里有 | 直接用 |
| `NIKE_COMMERCE_COUNTRY` | **0 命中** | `Cookies.TryGetValue` 可选读，读不到只是不设 `country` 变量 |
| `ffid` | **0 命中** | 只出现在 Farfetch 的文档注释里（"client id issued on first page load"） |
| `sbsd` | **无同名 cookie** | 池子里有 `/sbsd` 与 `_sbsdContext`，所以当年看着像真的 |

三条都已标 `inferred: no image evidence (R297)`，并由 `CookieEvidenceRatchetTests` 看着（2 条断言：条数不增长 + 每条仍在用且仍带标记）。

**性质**：三条都是**可选读**，缺失只会退化、不会崩 —— 所以保留，但标清楚。

---

## R298：查询参数名 —— 42 个里 38 有证据，4 个已标推断

| 参数 | 池子 | 备注 |
|---|---|---|
| `json` | 无 `json=` | 验证码驱动用 |
| `orderID` | 只有 `dwfrm_billing_paypal_paypalOrderID`（**含**它，但不是它） | Demandware |
| `siteId` | 只有 `get__siteId`（是 getter 名） | Demandware |
| `productTemplateId` | **0 命中** | GOAT；当前只在文档里作为一句话存在 |

四条都已标 `inferred: no image evidence (R298)`，由 `QueryParamEvidenceRatchetTests` 看着。

**`orderID` / `siteId` 这两条正是最危险的那类**：池子里有"包含它"的长名字，
读起来像有证据，其实那是别的东西的名字。

---

## 三类的合并账（R296–R298）

| 类别 | 总数 | 有证据 | 已标推断 |
|---|---|---|---|
| 端点 | 89 | 67 | **18**（+4 已改名/内部诊断单列） |
| 请求头 | 16 | 13 | 1（改名已修） |
| cookie | 5 | 2 | **3** |
| 查询参数 | 42 | 38 | **4** |

**四类合计：152 个"会发出去的东西"，25 个已标推断。**

---

## R299：18 条"无证据"必须拆成两类 —— **10 条真的发了，7 条只是文字**

查每一条到底出现在**代码里**还是**文档注释里**：

| 类 | 条数 | 含义 | 严重度 |
|---|---|---|---|
| **真的会发出去** | **10** | 代码里 `PostJsonAsync(Origin(c.Url) + "/v1/buys", …)` 这种 | **高**（真请求、无出处） |
| **只出现在文档注释** | **7** | 对商店行为的**文字描述**，复刻件并不发这个请求 | 中（是"断言"，不是"行为"） |

### 最扎眼的那条其实不发

`/api/beast` —— 我上一轮点名说它"基本可以断定是编的"。
这一查发现：它只出现在 `BstnFlow.cs` 的**文档注释**里（"Registered against ShopifyFlow until a live capture
showed otherwise: GET /api/beast/geoIP …"），**代码并不发它**。

> 也就是说：我上一轮把一个**观察记录**当成了**伪造请求**。

### 真正的 10 条（会发，且无池子证据）

`/account/recover`、`/account/verify`、`/api/checkout/v1/basket/{basketId}`（含 `/place-order`、`/shipping`）、
`/api/preorder/entry`、`/api/stock`、`/collections/new-releases`、`/rest/V1/carts/mine/totals`、`/v1/buys`

`EndpointEvidenceRatchetTests` 已改成两张表：**Sent ≤ 10**、**DocumentedOnly ≤ 7**。

### 关于那 7 条文档断言

它们的证据来源不是字符串池，而是**现场抓包/页面观察**（注释里就是这么写的）。
这类证据**不进池子**（路径是运行时拼的），所以"池子里查不到"并不能否定它们 ——
但也不能当已证实。**记为"待运行时复核"。**

---

## R321：GOAT 的 CSRF 端点——**这一次是"账本反过来帮了我"**

查 `/v1/buys` 有没有出处时，顺手看了 GOAT 在池子里到底有什么：

```
web-api                                  7 处
  https://www.goat.com/web-api/get-csrf-token     ← 有出处
web-api/v1/buys                          0 处
web-api/v1/countries                     0 处
buy_bar_data / product_variants          0 处
```

于是两件事同时成立：

1. `/v1/buys` 仍然**无出处**（账本判定不变，GOAT 的 `/web-api/` 前缀有出处，具体路径没有）；
2. 但复刻件取 CSRF token 的方式（cookie `XSRF-TOKEN` 或 meta 标签）**没有用上那个有出处的端点** ——
   已在 `GetHomeAsync` 里加**兜底**：cookie/meta 都拿不到时，GET `/web-api/get-csrf-token` 取回。

**兜底而不是替换**：cookie/meta 是浏览器会话本来就给的，端点只是页面没给时的退路。

---

## R323：把"有出处但没被用上"的路径列出来（每个商店一张）

方法是 R321 顺出来的：**为了证明某条路径没出处，先把该商店在池子里有出处的清单拉全**。

### GOAT（`www.goat.com`，5 条有出处）

| 有出处的路径 | 复刻件用了吗 |
|---|---|
| `/web-api/get-csrf-token` | ✔ R321 加了兜底 |
| `/web-api/v1/addresses` | **✘** |
| `/web-api/v1/billing_infos` | **✘** |
| `/web-api/v1/login` | **✘** |
| `/web-api/v1/users/send_otp_token` | **✘** |

复刻件的 GOAT 用的是 `/v1/buys`、`/v1/buys/{id}`、`/v1/product_variants/buy_bar_data` —— **这三条都无出处**。

**含义**：GOAT 的"登录 / 地址 / 账单信息"这三块在原版里是有明确端点的，
而复刻件根本没建模它们 —— 这是**功能缺口**，不只是"路径没出处"。

### Farfetch / Magento / Scheels

- `farfetch.com/api` 在池子里 **0 处** → Farfetch 那 4 条无出处路径，连"该域名下有出处的路径"都不存在；
- `magento` 关键字 **0 处** → Magento 相关的 3 条同样无从对照（Magento 是自建站，域名各不相同）；
- `preorder` 只有 **Nike 的 `partner_cart_preorder`** 和 purpledotprice 两条，与 `/api/preorder/entry` 无关。

### 于是 10 条无出处端点分两类

| 类 | 条数 | 说明 |
|---|---|---|
| **同店有出处清单可用** | 4（GOAT 那 4 条未用的） | 可以照着做功能，不是"编的" |
| **店里没有任何出处** | 10 | Farfetch 4 / Magento 3 / PopMart 1 / Retail 1 / StoreFlow 1 |

**下一步**：优先做 GOAT 的 `addresses` / `billing_infos`（提交订单时需要），
而 `/api/beast` 那类"店里零出处"的保持标 `inferred` 不动。

---

## R328：GOAT 的 5 条有出处路径**全部在用**

| 路径 | 之前 | 现在 |
|---|---|---|
| `/web-api/get-csrf-token` | ✔（R321 兜底） | ✔ |
| `/web-api/v1/login` | ✘ | **✔ 新增 `LoginAsync`** |
| `/web-api/v1/users/send_otp_token` | ✘ | **✔ 新增 `SendOtpAsync`** |
| `/web-api/v1/addresses` | ✘ | **✔ 新增 `GetAddressesAsync` + `EnsureAddressAsync`** |
| `/web-api/v1/billing_infos` | ✘ | **✔ 新增 `GetBillingInfosAsync`** |

**路径有出处、请求体没有** —— 四个方法的注释都写明了这一点，`GoatAccountSurfaceTests` 也盯着。

接入点：`SubmitOrderAsync` 在确认购买前先 `EnsureAddressAsync`（GOAT 的购买以某个地址为键），
拿不到地址就早失败并给出可读原因，而不是让确认请求 4xx 却不解释。

**测试形态说明**：`NetClient` 是 sealed 且方法非虚，flow 的 HTTP 缝无法伪造（不为此引入接口抽象），
所以 `GoatAccountSurfaceTests` 是**源码级断言**（路径仍在、出处分明、body 标 inferred、地址检查已接上），
不是行为测试。这条限制写进测试注释里。
