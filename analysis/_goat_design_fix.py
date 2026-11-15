import io
p = r'D:\projects\cyber-reverse\replica\docs\CONTROL_DESIGN_GoatAccount.md'
t = io.open(p, encoding='utf-8').read()
old_start = t.index('## 三、设计（不猜请求体，只做"能力 + 证据注释"）')
old_end = t.index('## 四、接到哪里')
new = '''## 三、设计（**修正版**：按复刻件真实的 HTTP 通道，不虚构 `HttpCaller`）

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

'''
t = t[:old_start] + new + t[old_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('design corrected to the real HTTP path')
