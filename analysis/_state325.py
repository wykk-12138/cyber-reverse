import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 325 轮：把设计稿里**虚构的依赖**改回真实通道（不编译）

### 一、上一版设计稿有一个不存在的东西

它写了 `GoatAccountApi(HttpCaller caller)` —— **复刻件里没有 `HttpCaller`**。
真实通道是 `StoreFlow` 上的两个 protected static：

```csharp
protected static Task<NetResponse?> GetAsync(FlowContext c, string url, string tag, CancellationToken ct);
protected static Task<NetResponse?> PostJsonAsync(FlowContext c, string url, string json, string tag, CancellationToken ct);
```

### 二、改成什么

四个方法**放到 `GoatFlow` 自己身上**（它是 `StoreFlow` 子类，能直接用这两个 helper）：

```csharp
private Task<NetResponse?> LoginAsync(FlowContext c, string email, string password, CancellationToken ct);
private Task<NetResponse?> SendOtpAsync(FlowContext c, string email, CancellationToken ct);
private Task<NetResponse?> GetAddressesAsync(FlowContext c, CancellationToken ct);
private Task<NetResponse?> GetBillingInfosAsync(FlowContext c, CancellationToken ct);
```

**不引入新抽象** —— 这是最小改动，也避免"为了优雅而虚构一层"。

### 三、这次错在纸上（但错法一样）

R259（猜 API）与 R302（猜模型）都是在代码里错；这次是在**设计稿里**错。
三者同一个根：**没有先读那一行**。

### 四、这一轮没有编译

可用内存 4.52 GB。

### 五、这一轮的一句话

> 设计稿的价值在于"下一轮照着做"，所以**设计稿里的一个虚构类型，会让下一轮直接编译失败**。

> **写设计稿也要读源码 —— 它不是散文，是施工图。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 325 轮（修正 GOAT 设计稿：`HttpCaller` 不存在 → 改用 `StoreFlow` 的 `GetAsync`/`PostJsonAsync`）。

---

## GOAT 四端点：施工图已修正

`docs/CONTROL_DESIGN_GoatAccount.md` 第三节已改写：

- **不加新抽象**：四个 `private` 方法放在 `GoatFlow` 上（它是 `StoreFlow` 子类，
  直接用 `GetAsync(FlowContext, url, tag, ct)` / `PostJsonAsync(FlowContext, url, json, tag, ct)`）；
- 路径**有出处**（`/web-api/v1/{login,users/send_otp_token,addresses,billing_infos}`），
  请求体字段名**无出处** → 注释里标 `inferred`；
- 接入点：`SubmitOrderAsync` 缺 `goat.addressId` 时取地址；登录/OTP 只提供能力。

## 教训（第三次同类）

R259 猜 API、R302 猜模型、R325 猜依赖 —— 都是"没先读那一行"。
**这次错在设计稿里，但一样会让下一轮编译失败。**

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
缺口       17（绑定表口径）
Commit     44.5 GB / 可用 4.52 GB   ← 低于硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
