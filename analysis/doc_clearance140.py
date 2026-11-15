import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 中间那段补上了：检测 → 问策略 → 写回（第 140 轮）

`StoreFlow.DetectAsync` 早就把 vendor 记进 `antibot`，`AntiBotProtocol` 早就知道
Cloudflare 的 cookie 叫 `cf_clearance` —— **但中间没有人问策略要 token，也没有人把结果写回去。**

这和 R133/R134 在支付侧发现的缺口是**同一个形状**，值得把模式说出来：

> **检测在、存储在，中间的调用不在。**

### `CloudflareClearance.ApplyAsync`

```csharp
if (!IsCloudflare(c.Session)) return StepOutcome.Success();   // 别人家的墙不管
var (token, status) = await runner.GetAsync(pageUrl, ct);
c.Session.Vars["cloudflare.solverStatus"] = status;
if (token) { c.Session.Vars["cloudflare.clearance"] = token;
             c.Session.Cookies["cf_clearance"]      = token; }
else       { c.Emit(status, "antibot"); }        // 拒绝文案照原样发出，流程继续
```

**一次写两个地方**：会话变量（给本进程看）+ cookie（给下一次请求用）。

### 一条带状态码的实测

`SESSION_STATE` 里早有一行：

```
Cloudflare JSD  cf-solver.cybersole.io  401
```

这说明**这个主机是真的、可达的**，只是拒绝未认证的调用 —— 比 Kasada 那条路强：
Kasada 连主机都认不出来。所以这里把 401 写成常量并附一句人话：

```csharp
public const int ServiceStatusObserved = 401;
public const string ServiceStatusMeaning =
    "cf-solver.cybersole.io answers 401 to an unauthenticated call: the host is real and reachable, " +
    "the protocol needs credentials this workspace does not have";
```

**「有主机、没协议」比「什么都没有」更接近能实现** —— 而且这句话能让人接着往下查。

### 五条测试

清关成功（两处都写）、拒绝（只写状态不写 cookie）、别人家的墙不碰、
401 观测已记录、以及「检测与存储本来就是现成的」这条自证。
'''

if "## 中间那段补上了" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("clearance bridge documented")
else:
    print("already present")
