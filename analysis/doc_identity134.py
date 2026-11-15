import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 闭环：终于有东西**写**那三个会话键了（第 134 轮）

R133 教会网关**读** `browser.fingerprintKey` / `browser.timezoneOffsetMinutes`，
但工作区里**没有任何地方写它们** —— 读端存在、写端不存在，每次支付都退回按 UA 派生。

### `BrowserIdentity`：唯一写入者

```csharp
BrowserIdentity.Record(session, "task-9/profile-2", utcOffsetMinutes: 60);
// 写入三个键：
//   browser.fingerprintKey          = "task-9/profile-2"
//   browser.timezoneOffsetMinutes   = "60"
//   browser.fingerprintPayload      = "fingerprint-v1" | "fingerprint-v1-sans-ua"
```

三个键**一起写、一起读**，因为只有一个理由让它们分开：**它们只在同时正确时才有意义**。

### 为什么 key 必须是「同一条」

```csharp
var launcherFingerprint = BrowserFingerprint.ForProfile(profilePath);
BrowserIdentity.RecordProfile(session, profilePath, utcOffsetMinutes: -300);
var paymentFingerprint  = BrowserIdentity.Fingerprint(session);

Assert.Equal(launcherFingerprint, paymentFingerprint);   // LauncherAndPaymentAgree
```

**启动器用哪个 key 选屏幕，支付就必须用哪个 key 报屏幕。** 这条测试就是整条链存在的理由。

### 读端也收进同一个类

网关现在写的是 `BrowserIdentity.Fingerprint(c.Session)` / `.TimeZoneOffset(c.Session)`，
测试 `TheGatewayUsesTheSingleWriter` 断言网关里**不再出现** `"browser.fingerprintKey"` 这种字面量 ——
**一个键只有一种拼法**。

### 这一轮的一句话

> 上一轮我发现「规则没被执行」。这一轮发现更深一层：**读的人有了，写的人根本没有。**
>
> **一个只被读取的变量，不是配置，是悬念。**
'''

if "## 闭环：终于有东西**写**那三个会话键了" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("identity closure documented")
else:
    print("already present")
