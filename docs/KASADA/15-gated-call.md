# 15 · 第二层判据实测：`cart.get` 200（HK 出口，同一会话）

> 这一份只记**实测**，不记推测。每一条都能用 §6 的命令重跑。
> 结论先行：**HK 出口能解，也能过 `cart.get`。之前那份"HK 被 SigSci 拦"的归因是错的**，
> 错在我构造的请求本身，错在三层，与节点无关。

---

## 1. 为什么要重做这件事

上一轮把 `cart.get` 的 429 读成"Signal Sciences 拦了 HK 出口"。证据是响应头
`orig-backend: F_sigsci_waf` 加空 body。**那不是证据，那是把同一个响应解释成了两种东西**：

- `orig-backend: F_sigsci_waf` 只说明这个响应**经过** SigSci 的 WAF 层（全站都经过），
  不说明是 WAF **拒绝**的；
- 空 body 也不区分"WAF 沉默拒绝"和"应用层 200 但内容为空"。

真因是：**那个请求不是一次合法的 `cart.get` 调用**。分成三层，任何一层都能单独让它失败。

---

## 2. 接口的真实形状（由服务端自己的错误信息逼出来）

`/api/cart.get` 是个 **tRPC 风格的 query procedure**，superjson 信封。

### 第一层：方法是 GET，不是 POST

```
POST /api/cart.get   ->  405
{"error":{"json":{"message":"Unsupported POST-request to query procedure at path \"cart.get\"",
 "code":-32005,"data":{"code":"METHOD_NOT_SUPPORTED","httpStatus":405,"path":"cart.get"}}}}
```

它自称 *query procedure*。**query 用 GET 读。**

### 第二层：input 走 `?input=`，且是 `{"json": ...}` 信封

裸对象直接塞 `?input=`：

```
{"code":"invalid_type","expected":"object","received":"undefined","path":[],"message":"Required"}
```

`received: undefined` 是关键：**整个 input 塌成 undefined**，不是"缺某个字段"。
这正是 superjson 解包时找不到 `json` 键的行为。所以查询串里必须是

```
?input={"json":{"country":"us","language":"en","viewContext":"Cart"}}
```

（`encodeURIComponent` 之后送）。这个形状与 arcbot `checkout/site.rs` 一致 ——
他们那边写成"用 `{"json":{...}}`"，一直被当成"请求体"，其实是 **input 信封**。

### 第三层：国家码是小写

`{"json":{"country":"US",...}}` 的应答把整个枚举吐了出来：

```
{"received":"US","code":"invalid_enum_value",
 "options":["at","be","ch","cn","cz","de","dk","es","fi","fr","gb","ie", ...]}
```

**`received` 有值，说明字段读到了、走到校验了。** 只是拼写不对，全都小写。

---

## 3. 实测结果（一次运行，同一会话，同一节点）

```
page = https://arcteryx.com/us/en/shop/X000009417
wire bytes (CDP loadingFinished) = 627,142 across 58 requests
requests dropped locally = 39
tl st = 1795087355907
TlSolved = True   TlBody = [{"reload":true}]
Ok      = True

--- cart.get, fired inside the solved session ---
S in-page POST, sensor stamps   : status=405  METHOD_NOT_SUPPORTED
P in-page POST, headers attached: status=429  (空 body)
G in-page GET {"json":...}      : status=200  len=448
```

`G` 那一臂的正文：

```json
{"result":{"data":{"json":{
  "id":"WGzhPDr98FAfF323ajvivZKUz0M8rcag",
  "totalQuantity":0,"email":null,"currencyCode":"USD","cartItems":[],
  "shippingAddress":null,"billingAddress":null,"promo":null,
  "totals":{"subtotal":0,"total":0,"tax":0,"taxPercentage":0,"discount":0},
  "shippingMethod":null},"meta":{...
```

真实 cart id、`currencyCode: USD`、完整购物车结构。**判据第二层达成。**

---

## 4. 三个附带结论（比 200 本身更值钱）

### 4.1 手挂 `x-kpsdk-ct` 比不挂更糟

同样是 POST：`S`（让传感器自己挂）→ **405 应用层应答**；`P`（手工 `Object.assign` 一个 ct）→ **429 空 body**。

**不挂 ct 能到应用层，挂了反而被 WAF 挡。** 机理是 ct 与会话绑定：传感器签发的 ct
配它自己的 `x-kpsdk-cd`、cookie、以及它算出来的请求序列；从外面塞一个 ct 进去，
组合不自洽，SigSci 直接拒。

⇒ 结论：**token 不能"带上"，只能"由产生它的那一端来挂"。** 这也是 arcbot 的 `cart.get`
为什么要走页面上下文而不是 host socket 的原因。

### 4.2 host 侧自建请求永远测不出 token

`H host-side POST` 一路 429。它和浏览器的差别不在 token，在 cookies、client hints、
TLS/HTTP2 指纹、Origin/Referer。**用它的结果去判节点的可用性，是把客户端的问题算到网络上。**

### 4.3 页面自己根本没调 `cart.get`

`page's own /api calls:` 是空的。产品页不会打购物车接口，所以"从页面观察里找 cart.get 的
正确形状"这条路本身不成立 —— 它的形状只能靠**制造一次调用**逼出来，这也是 §2 的
三层错误信息能拿到手的原因。

---

## 5. 判据三层，现在的状态

| 层 | 判据 | 状态 | 证据 |
|---|---|---|---|
| 一 | `/tl` 正文 = `{"reload":true}` | ✅ 每轮都过 | §3 |
| 二 | `cart.get` 200 | ✅ **本轮达成** | §3 的 `G` 臂正文 |
| 三 | 写接口的 PoW 严格校验 | ⬜ 未测 | 需 `cart.add` 一类 mutation |

层二的读取是宽松的（负对照也可能 200），所以它证明的是**形状对了**，
不是"token 不可伪造"。严格的证明在层三。

---

## 6. 重算命令

```powershell
cd D:\projects\cyber-reverse
$env:DOTNET_ROOT='D:\tools\dotnet8'
$env:KASADA_BUNDLE_OUT='.tmp-bundle.json'
# 可选覆盖：
#   KASADA_PAGE        默认 https://arcteryx.com/us/en/shop/X000009417
#   KASADA_STORE       默认 arcteryx
#   KASADA_CART_URL    默认 https://arcteryx.com/api/cart.get
#   KASADA_CART_BODY   默认 {"country":"us","language":"en","viewContext":"Cart"}
& D:\tools\dotnet8\dotnet.exe exec analysis\kasada-live\bin\Release\net8.0\kasada-live.dll --browser
```

看三行：`TlSolved`、`G in-page GET {"json":...}` 的 `status=200`、以及它正文里的 `id`。

---

## 7. 这一轮改了什么代码

- `analysis/kasada-live/Program.cs`
  - **默认站点从 `nike.com` 换成 Arcteryx 产品页**。之前每次忘了传参的分析都去开 Nike 页面，
    那不是任何人在测的东西。现在 `KASADA_PAGE` 可覆盖，`Store` 跟着 `KASADA_STORE` 走，
    两者不可能再不一致（原先是 L11 的 URL 和 L226/L330 的 `"nike"` 各写一遍）。
  - `cart.get` 探测从 host 侧挪进 `AfterSolveAsync` 钩子，在浏览器销毁前、同一会话里发。
- `replica/src/Cybersole.Stores/Scripts/ChromiumKasadaSolver.cs`
  - 新增 `AfterSolveAsync`（`Func<ChromiumBridge, CancellationToken, Task>?`）与 `AfterSolveError`。
    这是**产品逻辑该有的扩展点**，不是测试钩子：token 只有对它自己的会话才有意义，
    cookies / client hints / 连接指纹在 profile 关闭时全部消失，要用就必须在这个窗口里用。
  - `EvaluateAfterRunAsync` 增加 `awaitPromise` 透传（页面 fetch 是 Promise）。
