import io
p = r'D:\projects\cyber-reverse\replica\docs\CONTROL_DESIGN_GoatAccount.md'
t = '''# 功能设计：GOAT 的账号/地址四端点（R324 设计稿）

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

## 三、设计（不猜请求体，只做"能力 + 证据注释"）

新增一个**纯 HTTP 客户端**，不改 `IStoreModule`：

```csharp
// src/Cybersole.Stores/Flows/GoatAccountApi.cs
public sealed class GoatAccountApi
{
    public GoatAccountApi(HttpCaller caller);        // 复用流程里的 GetAsync/PostJsonAsync 通道

    public Task<StepOutcome> LoginAsync(FlowContext c, string email, string password, CancellationToken ct);
    public Task<StepOutcome> SendOtpAsync(FlowContext c, string email, CancellationToken ct);
    public Task<StepOutcome> GetAddressesAsync(FlowContext c, CancellationToken ct);
    public Task<StepOutcome> GetBillingInfosAsync(FlowContext c, CancellationToken ct);
}
```

**关键纪律**：四条方法都只发"路径 + 已认证 cookie"，**请求体按字段名直译**并标注 `inferred`：

- `LoginAsync` → `POST /web-api/v1/login`，body `{ "email", "password" }`（字段名 `inferred`）；
- `SendOtpAsync` → `POST /web-api/v1/users/send_otp_token`，body `{ "email" }`（`inferred`）；
- `GetAddressesAsync` / `GetBillingInfosAsync` → `GET`（无 body）。

**路径有出处，请求体没有** —— 这一点必须在代码注释和账本里同时写明，不能混为一谈。

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
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('GOAT account design written')
