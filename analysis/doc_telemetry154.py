import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 有了发信人，而发信人**会挑地址**（第 154 轮）

R153 让 payload 能被构建，这一轮给它一个发送者。风险在于**发错地方**：一个主机没配或拼错的遥测器，
会把一份指纹发到某处然后报成功 —— 而且没人会注意到。

### 两道闸门

```csharp
public static readonly string[] AllowedHosts =
{
    "analytics.cybersole.io",
    "telemetry.cybersole.io",
};                      // R138 那十五个里的两个
```

1. **没地址就不发** —— 默认未配置，未配置给的是**理由**而不是静默成功；
2. **只发给记录过的两个主机** —— 其余按名字拒绝，连 `analytics.cybersole.io.evil.test` 这种
   后缀伪装也过不去；`api.cybersole.io` 也被拒（它不在允许表里）。

这与 `endpoint-provenance.py` 对店端点的规矩是同一条，只是这次用在 **Cybersole 自己的主机**上。

### 传输是注入的，所以能离线取证

```csharp
new SessionTelemetry(sinkUrl, post: (url, body, ct) => …)
```

测试因此能同时断言「发了什么」和「**没发**」：

| 测试 | 断言 |
|---|---|
| 无地址 | 传输**零调用**，`LastError` 含 `no sink configured` |
| 未知主机（四个候选含伪装后缀） | 传输**零调用**，理由含 `not one of the recorded hosts` |
| 两个允许主机 | 各发一次，body **逐字节等于** `SessionPayloadBuilder.Build(...)` |
| 传输返回 false | `transport refused the payload`，不抛 |
| 传输抛异常 | 记录消息，不抛 —— **遥测永远不在结账关键路径上** |
| 取消 | `cancelled` |

### 一条顺带的自检

两个允许主机**都不是 solver 主机**（`IsSolverHost` 为 false）—— 这份 payload 是遥测，不是解墙答案。

### 这一轮的一句话

> 上一轮我担心的是「算错」。这一轮担心的是「发错」——**算错会被测试抓住，发错不会**。
>
> **凡是会把数据送出边界的地方，边界本身必须是可枚举、可断言的常量。**
'''

if "## 有了发信人" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("telemetry documented")
else:
    print("already present")
