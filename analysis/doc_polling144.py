import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 轮询那条路落成代码：`PollingSolver`（第 144 轮）

上一轮从 `PollCaptchaAsync` 得出「至少一条路是轮询的」。这一轮把它做成可以用的东西。

### 为什么需要它

| 路 | 什么时候有结果 |
|---|---|
| 本地浏览器求解 | 求解完就有 —— await 是对的 |
| **服务** | 接单，**稍后**才回答 —— await 分不清「拒绝」和「还没好」 |

replica 之前全是同步 await，所以**服务第二次才回答**和**服务拒绝**在代码里长得一模一样。

### `PollingSolver`：探针 + 间隔 + 上限

```csharp
new PollingSolver(probe, mode, interval: 1s, attempts: 20)
```

- **厂商无关** —— 探针由策略给，模式由策略定，它只负责「再看一次」；
- **有上限** —— 放弃时的状态串带次数与秒数：`Polled 20 time(s) and gave up after 20s`；
- **可取消** —— `ct` 一触发立刻退出，不烧预算。

### 六条测试（间隔用毫秒，秒级完成，不假时钟）

| 测试 | 断言 |
|---|---|
| `ATokenOnTheThirdLookIsFound` | 第三次答出，状态写 `Polled 3 time(s)` |
| `AProbeThatNeverAnswersGivesUpOnBudget` | 恰好探 5 次后放弃 |
| `CancellingStopsThePoll` | 取消后不再探（≤3 次） |
| `TheBudgetIsReadable` | `Attempts` / `Interval` / `GiveUpStatus` 可读 |
| `TheModeComesFromTheStrategy` | 模式来自策略，不来自装饰器 |
| `ThePollingFactIsRecorded` | 与 R143 的 `PollCaptchaAsync` 事实对得上 |

### 这一轮的一句话

> 上一轮我读到 `PollCaptchaAsync` 这个名字，说「至少一条路是轮询的」。这一轮补上那个「轮询」。
>
> **一个方法名可以是证据，但只有把它写成方法，它才变成能力。**
'''

if "## 轮询那条路落成代码" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("polling documented")
else:
    print("already present")
