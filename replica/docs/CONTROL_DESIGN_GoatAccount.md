# 功能设计：GOAT 的账号/地址四端点（R324 设计稿）

## 一、证据

`www.goat.com` 在字符串池里有 5 条 `/web-api/...` 路径，其中 **4 条复刻件没用**：

| 路径 | 推断用途 | 依据 |
|---|---|---|
| `/web-api/v1/login` | 账号登录 | 名字直白 |
| `/web-api/v1/users/send_otp_token` | 发 OTP（登录第二步） | `users/send_otp_token` |
| `/web-api/v1/addresses` | 收货地址列表/新增 | 名字直白 |
| `/web-api/v1/billing_infos` | 账单信息列表/新增 | 名字直白 |

（复刻件在用但**无出处**的：`/v1/buys`、`/v1/buys/{id}`、`/v1/product_variants/buy_bar_data`。）

## 二、复刻件现状

`GoatFlow` 的步骤：`GetHome → FindProduct → FindVariant → ScrapeVariantAvailability → AddToCart → GetCart → GetCheckout → SubmitOrder`。
**没有登录、没有 OTP、没有地址/账单** —— 也就是说 GOAT 流程现在是"游客结账"，
而原版显然有账号体系（有 login 和 OTP 端点）。

`IStoreModule` 的契约（`Cybersole.Http/Stores.Abstractions.cs:95`）只有
`Monitor / Checkout / CreateChallenge`，**没有登录入口** —— 所以登录不该塞进 `IStoreModule`。

## 三、设计（**修正版**：按复刻件真实的 HTTP 通道，不虚构 `HttpCaller`）

设计稿第一版写了一个 `HttpCaller` 依赖 —— **复刻件里没有这个类型**。真实通道是：

```csharp
// StoreFlow.cs:1771 / 1789  —— 都是 protected static，拿 FlowContext 说话
protected static Task<NetResponse?> GetAsync(FlowContext c, string url, string tag, CancellationToken ct);
protected static Task<NetResponse?> PostJsonAsync(FlowContext c, string url, string json, string tag, CancellationToken ct);
```

所以四个方法**必须放在 `GoatFlow` 自己身上**（它是 `StoreFlow` 的子类，能直接用这两个 helper），
或者放进一个 `static` 辅助类并显式传入那两个委托。

**选择前者**（最小改动、不引入新抽象）：

```csharp
// GoatFlow.cs —— 四个方法，全部 private，只被 SubmitOrderAsync 或将来编排层调用
private Task<NetResponse?> LoginAsync(FlowContext c, string email, string password, CancellationToken ct);
private Task<NetResponse?> SendOtpAsync(FlowContext c, string email, CancellationToken ct);
private Task<NetResponse?> GetAddressesAsync(FlowContext c, CancellationToken ct);
private async Task<NetResponse?> GetBillingInfosAsync(FlowContext c, CancellationToken ct);
```

四条都只发"路径 + 已吸收的 cookie"：

- `POST /web-api/v1/login`，body `{ "email", "password" }` —— **路径有出处，body 的字段名 `inferred`**；
- `POST /web-api/v1/users/send_otp_token`，body `{ "email" }` —— 同上；
- `GET /web-api/v1/addresses`、`GET /web-api/v1/billing_infos` —— 无 body。

**"路径有出处、请求体没有" 必须在注释里写清**，否则下一轮会把两者混为一谈。

> 这一处修正本身也是教训：设计稿第一版虚构了一个类型 —— **和 R259/R302 是同一类错，只是这次错在纸上。**

## 四、接到哪里（有真实用处，但不改主流程）

- `GoatFlow.SubmitOrderAsync` 之前：若 `Session.Vars["goat.addressId"]` 缺失，
  调 `GetAddressesAsync` 取第一条的 id（**这是"用得上"的最小接入点**）；
- `GetBillingInfosAsync` 同理取 `billing_info_id`；
- 登录/OTP **只提供能力，不自动触发** —— 账号登录属于任务编排层，不在结账流程里。

## 五、验收标准

1. 四个方法各发一次请求到**确切路径**（用假的 `HttpCaller` 断言），URL 以 `/web-api/v1/...` 结尾；
2. `LoginAsync` / `SendOtpAsync` 的 body 含 `email`，且 `LoginAsync` 含 `password`；
3. 非 2xx → `StepOutcome.Fail` 且信息含状态码；
4. `SubmitOrderAsync` 在缺 `goat.addressId` 时会调用 `GetAddressesAsync`（可用假 caller 计数验证）；
5. 四条路径的注释都带 `path evidenced; body inferred`。

## 六、测试计划

`GoatAccountApiTests`（5 条，全部用假 `HttpCaller`，不联网）。

## 七、完成后的账本动作

- `docs/ENDPOINT_LEDGER.md`：GOAT 从"5 条有出处、1 条在用"变成 **5 条全在用**；
- 缺口数字**不变**（这四条路径不在绑定表里，绑定表只管 UI 成员）—— 明确写下来，避免误改 ceiling。
