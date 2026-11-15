import io
p = r'D:\projects\cyber-reverse\replica\docs\ENDPOINT_LEDGER.md'
t = io.open(p, encoding='utf-8').read()
add = '''
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
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('ledger updated with the split')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 299 轮：18 条"无证据"必须拆成两类 —— 我上一轮**冤枉了一条**

### 一、拆法

看每条到底在**代码里**还是**文档注释里**：

| 类 | 条数 | 严重度 |
|---|---|---|
| **真的会发出去** | **10** | 高 —— 真请求、无出处 |
| **只出现在文档注释** | **7** | 中 —— 是"断言"，不是"行为" |

### 二、我上一轮冤枉了 `/api/beast`

上一轮我写"这条基本可以断定是当年照着风格编的"。这一查：

```
BstnFlow.cs 文档注释：Registered against ShopifyFlow until a live capture showed otherwise:
                     GET /api/beast/geoIP / POST /api/beast/monetate …
```

**它只出现在文档注释里，代码并不发它。** 我把一条**观察记录**当成了**伪造请求**。

### 三、真正的 10 条（会发、无池子证据）

```
/account/recover  /account/verify
/api/checkout/v1/basket/{basketId}  …/place-order  …/shipping
/api/preorder/entry  /api/stock  /collections/new-releases
/rest/V1/carts/mine/totals  /v1/buys
```

`EndpointEvidenceRatchetTests` 改成两张表：**Sent ≤ 10**、**DocumentedOnly ≤ 7**。

### 四、那 7 条文档断言的证据来源

不是字符串池，是**现场抓包/页面观察**（注释里写着）。这类路径运行时拼接，**本来就不会进池子** ——
所以"池里查不到"既不能否定它们，也不能证实它们。**记为"待运行时复核"。**

### 五、验证

```
EndpointEvidenceRatchetTests   3 通过 / 0 失败
完整套件                       见下
```

### 六、这一轮的一句话

> 上一轮我把 18 条一口价叫"无证据"；这一轮发现其中 7 条根本不是我发的。

> **"没有出处"有三种：真发了没出处、只是写着没发、以及我根本没看懂它在哪。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')
