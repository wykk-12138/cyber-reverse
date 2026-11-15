### 两个克隆任务独立运行

R99 的 `Clone` 是深拷贝 + 新 id。R103 的 `Start all` 让状态跟上了。这轮验证**两者一起**：
两个同名、同 URL、不同 id 的任务，会不会抢同一个运行时槽。

### 为什么这值得查

`TaskEngine` 用 `ConcurrentDictionary<string, TaskRuntime>` 按 **id** 键控：

```csharp
private readonly ConcurrentDictionary<string, TaskRuntime> _runtime = new();
private TaskRuntime Ensure(BotTask task)
    => _runtime.GetOrAdd(task.Id, _ => new TaskRuntime { Task = task });
```

**如果键控用的是名字或 URL**，两个克隆会互相覆盖，第二个永远不跑。

而 `Start(task)` 里还有一道早退：

```csharp
if (rt.State is TaskState.Monitoring or TaskState.Waiting or TaskState.CheckingOut) return;
```

**如果两个任务共用一个 `rt`**，第二个 `Start` 会被这行直接挡回去。

### 实测

点 `Start all`：

```
Text "multi-product test copy: Monitoring"
[21] ListItem "multi-product test copy  [shopify]  Monitoring  …"
[22] ListItem "multi-product test  [shopify]  Monitoring  …"
```

**两行都是 `Monitoring`。** 没有被早退挡掉。

### 固化成测试

```csharp
[Fact]
public async Task TwoClonesRunInSeparateRuntimeSlots()
{
    var (listener, port) = StartStoreServer(inStock: false);
    …
    var first = Make("original");
    var second = Make("original copy");

    engine.StartAll(new[] { first, second });
    await Task.Delay(500);

    Assert.Equal(2, engine.Runtime.Count);
    Assert.Equal(2, engine.Runtime.Count(r => r.State == TaskState.Monitoring));

    // different ids, same URL — that is the whole point
    Assert.NotEqual(first.Id, second.Id);
    Assert.Equal(first.Product.Url, second.Product.Url);
}
```

**跑 506 ms，通过。**

三条断言各挡一类错：

| 断言 | 挡住什么 |
|---|---|
| `Count == 2` | 共用槽位（第二个把第一个覆盖） |
| `Count(Monitoring) == 2` | 早退挡掉第二个 |
| `Id 不同、Url 相同` | 测试自己写错（两个不同 URL 也算通过就没意义了） |

### 这一步在「验证任务真的会跑」这条线上是第三段

| 轮次 | 验证了什么 |
|---|---|
| R97 | 能打开编辑器、能创建任务、能落盘 |
| R98 | 能编辑、`ExtraProducts` 不丢 |
| R99 | 能克隆（深拷贝，新 id） |
| R103 | `Start all` 后状态从 `Idle` 变 `Monitoring`，`Stop all` 变 `Stopped` |
| **R105** | **克隆出来的两个任务各自独立跑** |

**从「代码里调了 StartAll」到「两个任务真的在各自的槽里跑」，用了三轮。**

### 验证

```
dotnet test      549 通过 / 0 失败 / 2 跳过   (+1 TwoClonesRunInSeparateRuntimeSlots)
release build    0 errors
store modules    PASS 61 registered
verify.ps1       VERDICT: all checks passed
```

---
