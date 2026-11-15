import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 第三层落地：3DS 画像**从浏览器指纹派生**（第 132 轮）

`DlpaProfile` 不是「另建一套值」，而是**从 `BrowserFingerprint` 推导**：

```csharp
DlpaProfile.From(fingerprint, utcOffsetMinutes, userAgent, language)
```

| 字段 | 来源 |
|---|---|
| `browserColorDepth` | `fingerprint.ColorDepth` |
| `browserScreenWidth` / `Height` | `fingerprint.ScreenWidth` / `ScreenHeight` |
| `browserTZ` | **分钟数**（`60` = UTC+1，与实测样本 `-60` 同口径） |
| `browserLanguage` | `en-US` |
| `browserUserAgent` | 传入的 UA，`-sans-ua` 时**整条不出现** |
| `threeDSCompInd` / `fingerprintAttempted` | 常量 `Y` / `false` |
| `challengeWindowSize` | `null`，直到选定挑战窗口 |

### 为什么必须「派生」而不是「拼装」

支付画像与浏览器**不一致**会被方案的risk engine 拒，而拒的样子和「卡被拒」一模一样 ——
**排查时根本分不出来**。所以：

```csharp
public bool AgreesWith(BrowserFingerprint fingerprint)
```

测试 `AProfileCannotDisagree`：用 `with { BrowserScreenWidth = "5120" }` 造一个不一致的画像，
断言 `AgreesWith` 为 false —— **能造出来，但会被抓住**。

### 两层的边界，用测试钉住

`TheLayersDoNotBleed` 断言 DLPA 里**没有** `HardwareConcurrency` / `DeviceMemory` / `PixelRatio`
—— 那是浏览器层的字段，混进来就说明实现串层了。

### `-sans-ua` 只影响一个字段

`TheSansUaPayloadDropsOnlyTheUserAgent`：带 UA 版 12 个键，不带版 11 个，
**其余每个值逐一同值**。这保证了两个变体描述的是同一台设备，只是 UA 的发送位置不同。
'''

if "## 第三层落地" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("dlpa layer documented")
else:
    print("already present")
