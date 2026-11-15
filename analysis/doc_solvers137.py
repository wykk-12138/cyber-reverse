import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 四条路落成代码：`IKasadaSolver` + 三个实现 + 一个 runner（第 137 轮）

上一轮只是把字符串记成表。这一轮把它变成可执行的东西。

### 一、接口和四个实现

```csharp
public interface IKasadaSolver {
    KasadaStrategy.Mode Mode { get; }
    Task<KasadaToken> GetAsync(string pageUrl, CancellationToken ct = default);
}
```

| 实现 | 模式 | 它做什么 |
|---|---|---|
| `ApiKasadaSolver` | `Api` | 向服务要；**地址靠注入** |
| `LocalKasadaSolver` | `Local` | 包住现有的 `ChromiumKasadaSolver` —— 只加接口，不加逻辑 |
| `NamedFallbackSolver(Fallback)` | `Fallback` | 报告 `Kasada-Fallback` |
| `NamedFallbackSolver(MobileFallback)` | `MobileFallback` | 报告 `Kasada-Mobile-Fallback` |

`KasadaToken` 把 **token 与来源模式绑在一起** —— 调用方必须知道拿到的是哪一路，
因为回退 token 能用，但它和「解出来的」不是一回事。

### 二、`ApiKasadaSolver` 为什么不写地址

字符串证明**存在远端服务**（`Kasada API down (Contact staff)` 不可能是本地失败的消息），
但**没有给出地址**。所以：

```csharp
public ApiKasadaSolver(string? endpoint = null, Func<…>? call = null)
public bool IsConfigured => !string.IsNullOrEmpty(_endpoint) && _call is not null;
```

未配置时直接返回 `Kasada API down (Contact staff)` —— **用镜像自己的运维文案，而不是编一个主机名**。
这和 `endpoint-provenance.py` 是同一条规矩。

### 三、runner 的顺序与放弃

```
Api → Local → Fallback → MobileFallback
```

「取」在「解」前面：取便宜，而且镜像给尝试编了号（`Getting Kasada (1)`、`(2)`）——
**编号只有在先试、且会重试时才有意义**。回退放最后，因为回退 token 是没人想要的东西。

全空时返回镜像自己的放弃文案，并把**经过的每条状态串起来**：

```
Failed getting Kasada | Failed solving Kasada (TL) | Kasada-Fallback |
Kasada-Mobile-Fallback | Failed Kasada (Retry limit reached)
```

### 四、八条测试

覆盖：顺序、第一个可用即止（后面的路**不被调用**）、回退 token 自带名字、
全空放弃串、未配置 API 的运维文案、配置后能出 api token、回退不许冒充别的模式、四个实现覆盖四种模式。

### 五、这一轮的一句话

> 上一轮我说「我把一条策略实现成了一个函数」。这一轮把它拆回策略：
> **接口 + 四个实现 + 一个 runner，每段都能单独测。**
>
> **承认结构缺失，比补上结构难 —— 因为承认的时候，代码看起来是能跑的。**
'''

if "## 四条路落成代码" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("kasada solvers documented")
else:
    print("already present")
