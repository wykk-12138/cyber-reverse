# 指纹层词汇对照（生成物 —— 不要手改）

由 `python tools/fingerprint_vocab.py` 生成。功能优先级 ③（请求与指纹层）。

`BrowserIdentity.cs` 里有 3 个 `const string` 与 0 个 payload 字面量。
而它们分两类：**从镜像来的** 与 **本工作自造的** —— 而这件事可查，因为池里有字符串数据（R1045 只证明它没有**符号**）。

## 一、对照是否成立

| 对照串 | 命中 | 结论 |
|---|---|---|
| `kpsdk` | **17** | Kasada's cookie prefix, known present |
| `datadome` | **15** | DataDome's host, known present |

**→ 对照成立**（两个已知串都 > 0），所以下表里的 0 可以读成「镜像里没有」，不是查询失败。

## 二、逐名对照

| 类别 | 名字 | 镜像命中 | 地址 | 判定 |
|---|---|---|---|---|
| payload | `fingerprint-v1` | **2** | `0x147034eac` | **有据** |
| payload | `fingerprint-v1-sans-ua` | **1** | `0x147034ee4` | **有据** |
| session key | `browser.fingerprintKey` | **0** | `—` | **镜像里没有** |
| session key | `browser.fingerprintPayload` | **0** | `—` | **镜像里没有** |
| session key | `browser.timezoneOffsetMinutes` | **21** | `0x143304658` | **有据** |

## 三、结论

**有据的**：2 个 payload 字面量在镜像里（`fingerprint-v1` `0x147034eac` · `fingerprint-v1-sans-ua` `0x147034ee4`），时区概念有 21 条命中（含 `TimezoneOffset` 属性与 `ParseTimeZoneOffset`）。

**自造的**：`browser.fingerprintKey` · `browser.fingerprintPayload` —— 那两个 session 变量名在镜像里 0 次。

**→ 而那不矛盾**：session 变量是**本工作内部**的传值约定（R133/R134 定的），原版用别的方式把同一件事带到支付层。所以那两个名字**不需要**有据，而它们**必须**与它们携带的值一致 —— 值有据，名字是本地约定。

**→ 而 payload 名有据**是更强的结论：复刻件与镜像用**同一个** payload 词汇，所以 `FingerprintLayers.PayloadFor` 的分支名不是猜的。
