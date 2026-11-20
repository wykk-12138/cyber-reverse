"""Log R1291: the HTTP layer's first measured item — TLS 1.3 is offered by the image and not by the replica."""

import io

B = """
## R1291 —— `Cybersole.Http` 首轮取证：**三项已对齐、一项真差异（TLS 1.3）**

### 一、镜像侧证据

| 地址 | 内容 | 含义 |
|---|---|---|
| `143159CBB` · `1431662D3` | `BouncyCastle.Cryptography(.dll)`、*Legion of the Bouncy Castle Inc. 2000-2026* | 原版 **用 BouncyCastle** —— 复刻件 `BouncyTls` 同库 |
| `146EB3A24` · `146EB3A6C` | `TLS_AES_128_GCM_SHA256` · `TLS_AES_256_GCM_SHA384` | **TLS 1.3 专属套件** ⇒ 原版能协商 1.3 |
| `14716EEAC` | *tls: at most 2 GREASE extensions are supported* | 原版实现 **RFC 8701 GREASE**，上限 2 |

### 二、复刻件现状（逐项核过）

| 项 | 复刻件 | 结论 |
|---|---|---|
| 同库 | `BouncyTls` 继承 BouncyCastle `DefaultTlsClient` | **对齐** |
| GREASE | `TlsProfile.Grease` 默认 **true**；`BouncyTls` 注 1 个 GREASE cipher（`0x0A0A`）+ 1 个扩展（`0x1A1A`）；`Ja3.IsGrease` 也有 | **对齐**（原版上限 2，复刻用 1+1） |
| TLS 1.3 套件名 | `BouncyTls.cs:250-251` 已映射 `0x1301`/`0x1302` | 名字有 |
| **协商 TLS 1.3** | `GetSupportedVersions()` 只返回 `TLSv12` | **差异** |

### 三、这条差异是什么、不是什么

**是**：原版在服务端支持时走 TLS 1.3，复刻件永远停在 1.2。对 JA3/TLS 指纹与握手字节都有影响。

**不是**："忘了写一行"。`DefaultTlsClient` 是 BouncyCastle **1.3 之前**的基类；换到 1.3 客户端要连
`GetCipherSuites` / `GetSupportedVersions` / 扩展 getter 一起换，属**结构性改动**，不能顺手改。

所以本轮在 `BouncyTls.GetSupportedVersions()` 上方**写明差异与地址、以及为什么不能顺手改**——
让下一个读这段代码的人不用再重新发现一遍。这是这条队列（两百多轮 0 提交）里第一个被定住的实测项。

### 四、验证

`Tls|Ja3|Http` **75/75**；构建 0 错。

### 五、下一块（`Cybersole.Http` 的继续）

按同样方法往下核：HTTP/2 帧与 HPACK 动态表、Brotli 字典、重定向与 Cookie 吸收、代理轮换。
**每一项都先到镜像里找可对照的字面量/结构，找不到就记 unknown，不凭"看起来合理"改。**

证据等级：Observation = 四个地址的字符串原文、`GetSupportedVersions()` 的返回值；
Inference = 「TLS 1.3 套件名 ⇒ 原版协商 1.3」；**Unknown** = 原版 1.3 握手的扩展顺序（需流量）。
"""

V = """
---

## 第 1291 轮：`Cybersole.Http` 首轮取证——三项对齐、一项真差异

- 镜像：BouncyCastle（`143159CBB`）· `TLS_AES_128/256_GCM`（`146EB3A24`/`6C`）· GREASE 上限 2（`14716EEAC`）。
- 复刻件：同库 ✅ · GREASE 1+1 ✅ · 1.3 套件名映射 ✅ · **协商只有 TLSv12 ❌**。
- 该差异属结构性（换 BC 1.3 基类要连 getter 一起换），本轮在代码里写明地址与原因，不顺手改。
- `Tls|Ja3|Http` **75/75**。
"""

H = """
## R1291 —— HTTP 层首个实测项：TLS 1.3 差异定住；全量待跑（定向 75/75）

Observation：
- `146EB3A24`/`146EB3A6C` = TLS 1.3 套件；`14716EEAC` = GREASE 上限 2；`143159CBB` = BouncyCastle。
- 复刻 `BouncyTls.GetSupportedVersions()` 仅 `TLSv12` ⇒ 真差异（结构性）。
- 已在 `BouncyTls.cs` 写明差异地址与「为什么要连 getter 一起换」。

下轮：换到 BouncyCastle 的 TLS 1.3 客户端基类（连带 getter），或先核 HTTP/2 帧与 HPACK 动态表。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
