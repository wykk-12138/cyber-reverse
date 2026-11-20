"""Log R1292: three readings in three rounds, and the file that settled it."""

import io

B = """
## R1292 —— 同一件事读了三轮才读对：**默认传输本来就与原版同源**

### 一、三轮的过程（都留在这里，因为错法本身是教训）

| 轮 | 结论 | 错在哪 |
|---|---|---|
| R1291 | 镜像用 BouncyCastle TLS，复刻件只 1.2 ⇒ 真差异 | 拿 `BouncyCastle.Cryptography.dll` 与 `TLS_AES_*` 相邻就下了"TLS 栈是它"的结论；`TLS_AES_*` 其实是 **SslStream 的套件名** |
| R1292 第一次 | 原版是平台传输，那复刻件是自写栈 ⇒ 结构性偏离 | 只看了 `BouncyTls.cs`，**没看 `NetClient.Transport` 的默认值** |
| **R1292 最终** | **默认 `TransportMode.SChannel` = `SocketsHttpHandler`，与原版同源；自写栈只在 `OwnTls` 时可达** | —— |

### 二、决定性证据（46 条字符串）

| 地址 | 字符串 |
|---|---|
| `1432D5FE6` | `SocketsHttpConnectionContext` / `SocketsHttpHandler` |
| `1433D4B8A` | `SslStream` |
| `1436F9152` | `Http2StreamWindowManager` |
| `146EA88EC` | `System.Net.Http.SocketsHttpHandler.Http2Support` |
| `146EA8B04` | `System.Net.SocketsHttpHandler.Http2FlowControl.DisableDynamicWindowSizing` |
| `144A7C56A` | `System.Net.SocketsHttpHandler.Http3Support`（原版连 HTTP/3 开关都带） |
| `146EA89FC` | `System.Net.Security.DisableTlsResume` |

而 `NetClient.cs:42` —— `public TransportMode Transport { get; set; } = TransportMode.SChannel;`，
`ClientFor` 里 `new SocketsHttpHandler`。

**⇒ 生产路径两边都是平台的 TLS/HTTP2/HTTP3。TLS 1.3、GREASE、H2 窗口全由平台给，不存在差异需要"补"。**

### 三、真正剩下的是什么

`OwnTls`（自写 BouncyCastle 栈 + `Tls12Client` + `BouncyH2Client`）是**可达但非默认**的路径，
它只提供 TLS 1.2，握手字节永远不会等于平台的。它的价值是**指纹实验**（改扩展顺序看服务端反应），
不是生产。这一点现在写在 `BouncyTls.GetSupportedVersions()` 上方，并标明三轮的错法。

### 四、教训（写进纪律）

**"某个类怎么实现" ≠ "运行时走哪条路"。** 下结论前先读**入口的默认值**（`NetClient.Transport`），
再读实现。R1291 花的这一轮，是因为跳过了这一问。

### 五、验证

`Tls|Transport|Ja3` **58/58**；构建 0 错。

证据等级：Observation = 七条地址与字符串、`NetClient.cs:42` 的默认值、`ClientFor` 里的 `new SocketsHttpHandler`；
Inference = 「生产路径同源」；**Unknown** = 原版是否真的启用 HTTP/3（只有开关字符串，无协商证据）。
"""

V = """
---

## 第 1292 轮：三轮读对同一件事——默认传输与原版同源

- 证据：`1432D5FE6` SocketsHttpHandler · `1433D4B8A` SslStream · `1436F9152` Http2StreamWindowManager ·
  `144A7C56A` Http3Support · `NetClient.cs:42` 默认 `TransportMode.SChannel`。
- 结论：生产路径两边都是平台 TLS/H2；自写 BouncyCastle 栈只在 `OwnTls` 可达，只提供 1.2，用于指纹实验。
- R1291 的"真差异"**撤回**：`TLS_AES_*` 是 SslStream 的套件名，不是 BouncyCastle 的表。
- 教训：先读入口默认值，再读实现。
- `Tls|Transport|Ja3` **58/58**。
"""

H = """
## R1292 —— 撤回 R1291 的 TLS 差异结论：默认路径已同源（SChannel）；自写栈仅 OwnTls 可达

Observation：
- `NetClient.Transport` 默认 `SChannel` → `new SocketsHttpHandler`；镜像同样带 SocketsHttpHandler/SslStream/Http3Support。
- `TLS_AES_128/256_GCM` 是 SslStream 套件名（非 BouncyCastle 表）。
- `Tls|Transport|Ja3` 58/58。

下轮：`OwnTls` 的定位写清后，继续 ③ 的下一块——Brotli 字典与重定向/Cookie 吸收；或转 ② 的 PayPal 3DS 阶段 2–8。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
