"""Log R1293: the HTTP layer's default path, measured property by property."""

import io

B = """
## R1293 —— ③ 收口：默认传输**六项逐一核对**，全部同类同源

### 一、`NetClient.ClientFor` 的 handler（`NetClient.cs:84-102`，逐行读过）

| 属性 | 复刻件取值 | 镜像侧对应证据 |
|---|---|---|
| `EnabledSslProtocols` | **`Tls12 \\| Tls13`** | `146EB3A24`/`6C`（SslStream 的 1.3 套件名） |
| `CipherSuitesPolicy` | `profile.BuildCipherPolicy()` | `1433D4B8A` `SslStream`（套件由 profile 定） |
| `ApplicationProtocols` | `profile.BuildAlpn()` | `146EA88EC` `SocketsHttpHandler.Http2Support` |
| `MaxAutomaticRedirections` | **10**（= `RedirectPolicy.DefaultMaxRedirects`） | `MaxRedirects` 是镜像里的设置名（`RedirectPolicy` 已记） |
| `AutomaticDecompression` | `All` | `gzip, deflate, br` |
| `UseCookies` + `CookieContainer` | 均启用 | `1432D5FE6` `SocketsHttpHandler` |

**⇒ 六项全部是平台同名属性，取值也与原版同类。③ 的默认路径没有待补的差异。**

### 二、由此**彻底收回** R1291

R1291 说"复刻件只 1.2 ⇒ 真差异"。真相是：默认路径 **`Tls12 | Tls13`**，
"只 1.2"仅对 `OwnTls`（自写 BouncyCastle 栈，`GetSupportedVersions()` 返回 `TLSv12`）成立，而它**需要显式选择**才可达。

三次修正的最终结论已写进 `BouncyTls.cs` 注释：六项属性名 + 三个地址 + `OwnTls` 的定位。下一个读这段的人
不必再把这条队列从头量一遍。

### 三、本轮另一处核实：Brotli 字典**已对齐**

`Compression/BrotliDictionary.cs` 的注释（R128 记录）已经写明：
镜像里资源名 `Cybersole.Http.Compression.BrotliDictionary.bin`、载荷在 **offset 0x62DD580**、
长度 **122,784**（正是 RFC 7932 规定的字典大小），开头字节解出 " of the " / " of " / " in " —— 标准前缀表。
复刻件**携带同一份字典**。限制也已记录：.NET 8 的 `BrotliDecoder`/`BrotliStream` 不暴露字典参数，
所以用它压缩的响应体目前解不了——这是**平台能力限制**，不是漏做。

### 四、验证

`Tls|Transport|Redirect|Brotli` **92/92**；构建 0 错。

### 五、③ 的结论与去向

`Cybersole.Http` 的**默认路径已与原版同源**（平台 TLS/H2/压缩/重定向/Cookie），
自写栈是可选实验路径。这条优先级可以从"欠账两百轮"降为"已核对，剩余为流量级证据缺口"。
**下一轮转 ②**：`PAYMENT_CHALLENGES.md` 的 PayPal 3DS 阶段 2–8。

证据等级：Observation = 六项属性逐行、三个地址、字典注释原文；
Inference = 「默认路径同源」；**Unknown** = 原版是否真启用 HTTP/3（只有开关字符串）、
Brotli 字典压缩体的真实响应样本（需 live capture）。
"""

V = """
---

## 第 1293 轮：③ 收口——默认传输六项逐一核对，全部同源

- handler 六项：`Tls12|Tls13` · `CipherSuitesPolicy` · `ALPN` · `MaxAutomaticRedirections=10` · `All` 解压 · `UseCookies`。
- **R1291 的"只 1.2"彻底收回**：那只对 `OwnTls` 成立，默认路径已启 1.3。
- Brotli 字典已对齐（122,784 B / offset 0x62DD580 / 标准前缀表），限制是 .NET 8 无字典 API。
- `Tls|Transport|Redirect|Brotli` **92/92**。
"""

H = """
## R1293 —— ③ 收口：handler 六项同源；R1291 结论彻底收回；转 ②

Observation：
- `NetClient.cs:84-102`：`EnabledSslProtocols = Tls12|Tls13`、`CipherSuitesPolicy`、`ALPN`、
  `MaxAutomaticRedirections=10`、`AutomaticDecompression=All`、`UseCookies=true`。
- `BrotliDictionary` R128 已取证：122,784 B、offset 0x62DD580、标准前缀表；限制已记（.NET 8 无字典参数）。
- 定向 92/92。

判断：③ 默认路径已同源，剩余只是流量级证据缺口（HTTP/3 是否真启用、Brotli 字典压缩体样本）。
下轮：**转 ②** —— PayPal 3DS 阶段 2–8（`PAYMENT_CHALLENGES.md`）。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
