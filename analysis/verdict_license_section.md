### `License`：POST 到一个 GET-only 端点，永远不可能成功

窗口只有两个按钮（`Verify` / `Close`），`VerifyAsync` 看起来完整——真的调用
`LicenseService.VerifyLicenseAsync`，真的 await，真的在成功时 `Config.Save()`。

**它不是假实现。它只是永远失败。**

### 实测

密钥格式要求：16–64 个 hex 字符。填 `0123456789abcdef0123456789abcdef`，点 `Verify`：

```
failed: verification failed (HTTP 405)
```

**405 = Method Not Allowed。**

### 探两个主机

```
GET  cybersole.io/api/apisecuretoken   -> 200
     {"token":"7/AIx6Wnq9PFDran.c5Iyg...==./lUDt8eWT8Er...=="}
POST cybersole.io/api/apisecuretoken   -> 405   Allow: GET

api.cybersole.io/auth/token            -> 404
api.cybersole.io/auth/login            -> 404
api.cybersole.io/me                    -> 404
api.cybersole.io/license               -> 404
api.cybersole.io/license/verify        -> 404
api.cybersole.io/health                -> 200  "Healthy"
api.cybersole.io/zzz-control           -> 404   ← 对照组
```

**`/zzz-control` 也 404，所以 404 是诚实的「路由不存在」，不是「这个路由需要认证」。**

**`api.cybersole.io` 上只有一个 `/health`。** 主站上只有一个 GET-only 的 token 端点。

### 那个 token 是什么

三次请求，**返回值完全一样**：

```
parts: 3   total len: 194
[0] 16 chars base64 -> 12 bytes   eff008c7a5a7abd3c50eb6a7      ← AES-GCM nonce 长度
[1] 88 chars base64 -> 64 bytes   73923280725fab90...           ← 密文
[2] 88 chars base64 -> 64 bytes   fe5503b7c7964fc1...           ← 签名（Ed25519 是 64 字节）
```

**二进制里 `AesGcm` 出现 2 次、`RSA` 出现 30 次。** 这是一个密封的配置/公钥 blob，
**不是 license 响应**。

### 原版的结构（从字符串恢复）

```
Cybersole.Ui.Views.Auth.LicenseControl
   Refresh      !Getter
   Dashboard    !Getter/!Setter
   Authenticate !Getter  (AsyncCommand)

Cybersole.Models.License
   Name  !Getter/!Setter
   Last4 !Getter

StrongAuthority
LicenseVerifier
InvalidLicenseException / NoLicenseException
```

**原版的 `Authenticate` 是一个 `AsyncCommand`，配 `LicenseVerifier` 和 `StrongAuthority` 两个类。**
它读那个密封 token，**用内置的密钥材料在本地验证**。

### 修成诚实的失败

```csharp
var res = await _http.GetAsync(SecureTokenUrl, _auth.Authorized("license"), ct);

if (!res.IsSuccess)
    throw new InvalidLicenseException(
        $"the licence endpoint answered HTTP {res.StatusCode}; it accepts GET only and "
        + "this build has no key material to open the sealed token it returns");

throw new InvalidLicenseException(
    "the licence endpoint returned a sealed token that this build cannot open. "
    + "Accepting the key anyway would be a fake activation, so it was rejected. "
    + $"Local format check passed for ****{Tail(licenseKey)}.");
```

**实测输出**：

```
failed: the licence endpoint returned a sealed token that this build cannot open.
Accepting the key anyway would be a fake activation, so it was rejected.
Local format check passed for ****cdef.
```

### 为什么这样改而不是「接受任何 key」

**这个窗口最危险的做法是让 `Verify` 无条件返回 true。**

那会让 `settings.json` 里出现 `license: <任意字符串>`，`HasLicense` 变成 true，
`ValidateOffline()` 通过——**用户会以为自己激活了**，直到某个依赖许可的功能真的去要权限。

**现在它明确说：格式对、端点通、但这个构建打不开密封 token。** 三句话都是真的。

### 这一类的名字

前面 37 个死按钮是「**没做**」。这一个不是——**它做了，方向错了**。

| 类型 | 例子 | 特征 |
|---|---|---|
| 没做 | `Status("...")` | 点了没反应 |
| 保存不落盘 | `Captcha Providers` | 重启就丢 |
| 表单被忽略 | `Cloudflare Providers` | 值不对 |
| **协议用错** | **`License`** | **永远失败，但代码看着完整** |

**第四种最难自查**：它没有语法错误、没有编译警告、调用链完整——**只有真的发一次请求才知道 405。**

### 验证

```
dotnet test      579 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
settings.json    license 已清空
```

---
