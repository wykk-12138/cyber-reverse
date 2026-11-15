import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 轮询接到两条服务路上了（第 145 轮）

R144 造了 `PollingSolver`，但它没接到任何地方。这一轮把两条服务路都改成可轮询。

### 一、两个工厂方法

```csharp
ApiKasadaSolver.Polling(probe, interval, attempts)
ServiceCloudflareSolver.Polling(probe, interval, attempts)
```

一次性的调用形式**保留**（`IsPolling == false`），因为**同步应答的服务仍然存在**。
两条路现在共享同一条判断：

```csharp
IsConfigured = _polling is not null || (endpoint && call);
```

### 二、为什么轮询形式**只收探针、不收地址**

```csharp
public static ApiKasadaSolver Polling(Func<CancellationToken, Task<string?>> probe, …)
```

**探针不是地址。** 所以 R137 那条规矩（没地址就不许编主机）在轮询形式下自动成立 ——
测试 `NoAddressStillMeansNoHost` 顺带断言源码里**不出现** `https://api.cybersole.io`。

### 三、空轮询要能掉到 in-bot

`AnEmptyPollFallsThroughToInBot`：服务路轮询 3 次全空 → 梯子继续 → in-bot 拿到 token →
状态仍是镜像那句 `Cloudflare solver refused the token, solving in-bot`。

**轮询没有改变梯子的顺序，只是让「服务那一路」有了等待的能力。**

### 四、五条测试

两条路都能轮询、迟到答案仍能出 token（状态带 `Polled 3 time(s)`）、
Cloudflare 那条按字符串接口返回、空轮询掉到 in-bot、无地址不许编主机。

### 五、这一轮的一句话

> R144 造了一个零件，R145 把它装上去。这两轮的差别，就是前面四轮反复踩的那件事：
> **零件存在 ≠ 零件在工作。**
>
> 不同的是，这次我**先造零件再接**，而不是先宣称接好了。
'''

if "## 轮询接到两条服务路上了" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("service polling documented")
else:
    print("already present")
