import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 三层的来源终于接上了：Kasada 求解器就是身份的出生地（第 135 轮）

整条链现在读得通了：

```
ChromiumBridge.LaunchAsync
   ├─ 建 profile 目录           →  ProfilePath
   └─ BrowserFingerprint.ForProfile(ProfilePath)
          ↓
ChromiumKasadaSolver.SolveAsync(…, FlowSession? session)
   ├─ ProfileKey = bridge.ProfilePath
   └─ BrowserIdentity.RecordProfile(session, bridge.ProfilePath, …, userAgentAlreadySent: true)
          ↓
AdyenGateway.BrowserInfo(c)
   └─ BrowserIdentity.Fingerprint(c.Session) → 同一个 key → 同一块屏幕
```

**在这之前，第一步对后两步是不可见的** —— token 求解所用的身份与支付所描述的身份
可以完全不同，而且**没有任何东西会报错**。

### 为什么 `userAgentAlreadySent: true`

求解器自己把 UA 发给页面（`ApplyStealthAsync` 会重写 UA 并注入），所以它记身份时选
`fingerprint-v1-sans-ua` —— **同一份 UA 不发两遍**，也不假设对方会去别处找。

### 测试的四条

| 测试 | 断言 |
|---|---|
| `TheSolverRecordsTheIdentity` | 记身份发生在 `NavigateAsync` **之前** |
| `TheBridgePublishesItsIdentity` | 桥暴露 `ProfilePath` / `Fingerprint` |
| `TheResultCarriesTheKey` | 无会话的调用方也能拿到 `ProfileKey` |
| `OneKeyOneFingerprintOneProfile` | 一个 key → 一个指纹 → 一份一致的 3DS 画像 |

### 这一轮的一句话

> 三层数据我做了四轮：先证明它们存在，再各自建类，再接线，再让写端存在。
> 这一轮才把「谁生成身份」和「谁使用身份」连成一条线。
>
> **数据模型正确，不等于数据流正确。**
'''

if "## 三层的来源终于接上了" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("identity chain documented")
else:
    print("already present")
