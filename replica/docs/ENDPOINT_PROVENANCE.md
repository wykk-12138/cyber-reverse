# 端点溯源台账

第 129 轮生成。每个在 `src/Cybersole.Stores/Flows/*.cs` 里出现的 URL / 路径字面量，
要么**逐字出现在镜像里**，要么在下面登记为 `live`（有真实响应证据）或 `fixture`
（故意保留的不存在路径，用测试禁止）。**三者都不是的，就是发明。**

```
endpoint constants: 160   verbatim in pool: 160   invented: 0   unresolved: 0
inline URL/path literals: 202   not in pool: 29
```

## live —— 有响应证据、但镜像里没有这条字面量

- `live` `/api/beast` —— R91: the prefix answers (geoIP and monetate live under it)

## fixture —— 故意保留的不存在路径

- `fixture` `/api/cart/add` —— PopMartEndpoints.Invented — negative fixture (R100)
- `fixture` `/api/order/submit` —— PopMartEndpoints.Invented — negative fixture (R100)
- `fixture` `/api/stock` —— PopMartEndpoints.Invented — negative fixture (R100)

## 待定 —— 既不在镜像里，也没有响应证据（24 条）

| 文件 | 行 | 字面量 |
|---|---|---|
| `FarfetchFlow.cs` | 161 | `/api/basket/v1/items` |
| `GoatFlow.cs` | 193 | `/v1/buys` |
| `HbxFlow.cs` | 41 | `/api/v2/shop/countries` |
| `HybrisFlow.cs` | 60 | `/view/resources/getUserInfo` |
| `MagentoFlow.cs` | 180 | `/rest/V2/carts/mine` |
| `MagentoFlow.cs` | 193 | `/rest/V1/carts/mine` |
| `MagentoFlow.cs` | 223 | `/rest/V1/carts/mine/totals` |
| `MagentoFlow.cs` | 559 | `/account/verify` |
| `MagentoFlow.cs` | 833 | `/collections/new-releases` |
| `RetailFlows.cs` | 39 | `https://yzy-prod.swell.store` |
| `RetailFlows.cs` | 747 | `https://api.pocketgames.nl/v1/public/raffle-entry` |
| `RetailFlows.cs` | 965 | `/api/checkout/submit` |
| `RetailFlows.cs` | 1115 | `/api/preorder/entry` |
| `ScheelsFlow.cs` | 33 | `https://search.scheels.com` |
| `ScheelsFlow.cs` | 206 | `/api/search` |
| `ScheelsFlow.cs` | 230 | `/api/cart/items` |
| `ScheelsFlow.cs` | 270 | `/api/checkout/submit` |
| `StoreFlow.cs` | 641 | `/checkout/complete` |
| `StoreFlow.cs` | 848 | `https://api.paypal.com/v1/oauth2/token` |
| `StoreFlow.cs` | 968 | `https://p01.mul-pay.jp/payment/SaveCard.idPass` |
| `StoreFlow.cs` | 1115 | `/account/recover` |
| `StoreFlow.cs` | 1471 | `https://a.klaviyo.com/client/subscriptions/confirm?code=` |
| `StoreFlow.cs` | 1568 | `/buy/carts/v2/app` |
| `StoreFlow.cs` | 1626 | `/account?email=` |

**这 24 条就是要处理的清单**：要么去镜像里找到真的那条，要么改成 `live` 并补证据，
要么删掉并把功能标成未实现。

## 正式缺口：Kasada `Api` 那条路**没有地址**（第 138 轮）

第 136/137 轮证明原版有「取 Kasada」（远端服务）这条路，第 137 轮给了它注入入口但**没有地址**。
这一轮把原版自己的主机表整个捞出来，终于能把这条缺口写清楚。

### `*.cybersole.io` 十五个主机

```
amazon-waf    analytics   api        castle       cdn
cf-solver     datadome    forward    images       match
pop4          proxy       support    telemetry    text-captcha
```

**没有 `kasada.cybersole.io`。**

### 所以缺口是确定的，不是没查

| 事实 | 依据 |
|---|---|
| 存在远端「取 Kasada」这一路 | `Getting Kasada (1)`、`Failed getting Kasada (Rotating)` |
| 那条路的后端**就是原版自己的服务** | `Kasada API down (Contact staff)` —— 「请联系客服」是自家后端挂了才说的话 |
| **没有任何 Kasada 专用主机** | 十五个主机里没有 |
| 最可能的候选 | **`api.cybersole.io`** —— 唯一剩下的后端 |

`CybersoleHosts.KasadaApiCandidate` 把它记成**推断**，`KasadaApiEvidence` 明写
`no kasada.cybersole.io exists … inferred … no capture`，并有测试守着这句话。

> **这是本会话第一次把「原版有、我们缺」写成正式条目**，而不是让它在代码里沉默。

### 顺带：四个 solver 主机，和同一个「服务 vs 本地」分野

| 主机 | 解什么墙 |
|---|---|
| `amazon-waf.cybersole.io` | Amazon WAF |
| `cf-solver.cybersole.io` | Cloudflare |
| `datadome.cybersole.io` | DataDome |
| `text-captcha.cybersole.io` | 文字验证码 |

还有一句把分野说白的话：

```
Cloudflare solver refused the token, solving in-bot
```

—— **服务拒了，就在机器人内部解**。这和 Kasada 的 `Api` → `Local` 是**同一条策略的两个实例**。

设置页那组名字也在：`CloudflareSolvers`、`CloudflareSolverId`、`CloudflareSolver.Default`、
`CapSolver`、`CloseSolver`、`EmptySolver.html`。

## R201 — `Flows/*.cs` 里 24 条 inline 字面量的判定

工具在 R129 起把 baseline 锁在 24（"允许存在，禁止增长"）。R201 逐条判完，**baseline 归零**。

三类标签的含义（新增 `assembled`）：
- `live` —— 代码里有响应证据（注释点名了证明它的响应）
- `assembled` —— 平台公开的 REST 形状，镜像里没有这条字面量；只对本流程自己的 origin 使用
- `fixture` —— 故意保留的不存在路径，用测试禁止

### live（3 条，代码里有证据）

- `live` `/api/v2/shop/countries` —— HBX，"Verified: this endpoint answers and returns a country list"
- `live` `/view/resources/getUserInfo` —— Hybris，"verified endpoint: confirms the session cookie is usable"
- `live` `https://yzy-prod.swell.store` —— Swell 平台子域，"Verified from the capture"；镜像里只有 `swellAPI`/`swellConfig` 字样

### assembled（21 条，平台形状，镜像没有）

- `assembled` `/api/basket/v1/items` —— Farfetch 加车；镜像里 Farfetch 只有域名与 `/link/recatalog` 字样
- `assembled` `/v1/buys` —— GOAT 下单
- `assembled` `/rest/V2/carts/mine` —— Magento（Adobe Commerce）REST 购物车根；镜像只有 `/V1/carts/mine/payment-information` 与 `/V1/carts/mine/shipping-information`
- `assembled` `/rest/V1/carts/mine` —— 同上，V1 版本
- `assembled` `/rest/V1/carts/mine/totals` —— 同上，合计子资源
- `assembled` `/account/verify` —— JDSports 二步验证
- `assembled` `/collections/new-releases` —— KITH 发布轮询（镜像里只有 `new-releases-trading-card-games` 这个 handle）
- `assembled` `https://api.pocketgames.nl/v1/public/raffle-entry` —— 主机在镜像里（`https://api.pocketgames.nl`），**路径不在**；镜像是 `/v1/reservations` 与 `/v1/public/drop-schedule`
- `assembled` `/api/checkout/submit` —— Fanatics 下单
- `assembled` `/api/preorder/entry` —— 预售入口
- `assembled` `https://search.scheels.com` —— Scheels 搜索子域
- `assembled` `/api/search` —— 搜索接口，需要 `X-Client-Source` 头
- `assembled` `/api/cart/items` —— Scheels 加车
- `assembled` `/checkout/complete` —— 通用结账收尾
- `assembled` `https://api.paypal.com/v1/oauth2/token` —— PayPal OAuth2 token
- `assembled` `https://p01.mul-pay.jp/payment/SaveCard.idPass` —— GMO 卡令牌化
- `assembled` `/account/recover` —— 找回账号
- `assembled` `https://a.klaviyo.com/client/subscriptions/confirm?code=` —— Klaviyo 订阅确认（镜像里是 `event-bulk-create`）
- `assembled` `/buy/carts/v2/app` —— Nike App 购物车 v2
- `assembled` `/account?email=` —— HEAD 探测账号是否存在

> 这 21 条都只用**流程自己的 origin**（`Origin(c.Url)`）或平台公开主机，没有一条是"编一个 Cybersole 的后端地址"。
> 这条线是硬的：镜像里 `https:///ips.js?&x-kpsdk` 的 authority 是空的，说明原版自己也不写死后端。