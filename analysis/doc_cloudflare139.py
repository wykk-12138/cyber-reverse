import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## Cloudflare 是**同一条梯子**：服务 → in-bot（第 139 轮）

上一轮我说 `Cloudflare solver refused the token, solving in-bot` 与 Kasada 的 `Api → Local`
「是同一条策略的两个实例」。这一轮把它变成代码，验证这句话。

### 一、两个模式，一条梯子

| 模式 | 谁干活 | 地址 |
|---|---|---|
| `Service` | `cf-solver.cybersole.io` | **有**（十五个主机之一） |
| `InBot` | 已开着页面的浏览器 | 无（本地） |

```csharp
CloudflareStrategyRunner.Default(serviceCall, inBotSolve)
// 顺序：Service → InBot
```

**拒绝不是错误，是继续往下走的理由** —— 所以 runner 把 `RefusedMessage` 当**状态**返回，
而不是失败。

### 二、与 Kasada 对齐的地方

| 维度 | Kasada | Cloudflare |
|---|---|---|
| 服务路 | `Api`（地址**缺**，候选 `api.cybersole.io`） | `Service`（地址**有**） |
| 本地路 | `Local` | `InBot` |
| 额外路 | 两个具名回退 | 无 |
| 接口 | `IKasadaSolver` | `ICloudflareSolver` |
| 拒绝文案 | `Failed getting Kasada` | `Cloudflare solver refused the token, solving in-bot` |

`CloudflareAndKasadaHaveTheSameShape` 断言两者**服务在前、本地在后** —— 这就是那条原则。

### 三、协议是注入的，主机是记录的

服务的**协议**镜像里没有，所以 `ServiceCloudflareSolver` 的调用是注入的；
但它的**主机**有 —— `cf-solver.cybersole.io`，而且 `CybersoleHosts.WallFor` 能说出它解的是 Cloudflare。
**能和不能，分得清清楚楚。**

### 四、cookie 与注册表

- `cf_clearance` —— 与 `AntiBotProtocol.CookiesFor("Cloudflare")` 一致（测试对得上）；
- 设置页那六个名字（`CloudflareSolvers` / `CloudflareSolverId` / `CloudflareSolver.Default` /
  `CapSolver` / `CloseSolver` / `EmptySolver.html`）已入表。

### 五、这一轮的一句话

> 上一轮我把一句话当成**证据**。这一轮把它当成**规格**：照着它写出两个模式和一条顺序，
> 然后测试确认「服务在前、本地在后」。
>
> **一句话可以是证据，也可以是需求 —— 区别只在于你拿它来「相信」还是拿它来「实现」。**
'''

if "## Cloudflare 是**同一条梯子**" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("cloudflare ladder documented")
else:
    print("already present")
