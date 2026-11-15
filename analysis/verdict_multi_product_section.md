### 多商品任务：一个任务现在能监控多个 URL

上轮点开原版面板发现 `Cart` tab 有 `Add Input` 行，而 `BotTask` 只有单个 `Product`。
这轮补上了。

### 改动是「加」不是「改」

```csharp
/// Further products this task monitors, beyond Product.
/// The original's task creator has an "Add Input" row on its Cart tab, so one task can carry
/// several product URLs. The replica only ever had the single Product, which is why this exists
/// as an addition rather than a change: Product stays the primary entry so every existing
/// consumer keeps working, and AllProducts is what a caller should use when it wants all of them.
public List<Product> ExtraProducts { get; set; } = new();

[JsonIgnore]
public IReadOnlyList<Product> AllProducts =>
    ExtraProducts.Count == 0
        ? new[] { Product }
        : new[] { Product }.Concat(ExtraProducts).ToList();
```

**为什么保留 `Product`**：`TaskEngine`、`ExportService`、`FlowStoreModule` 都在用它。
改成 `List<Product>` 会波及六处，而收益只是省一个字段。

**为什么 `AllProducts` 永不返回空**：`TaskEngine` 用取模索引它，空列表会除零。
`Product` 有初始化器（`= new()`），所以单商品任务也一定有一个元素。

### `TaskEngine` 改成 round-robin

```csharp
var products = task.AllProducts;
var productIndex = 0;

while (!ct.IsCancellationRequested)
{
    var current = products[productIndex % products.Count];
    productIndex++;

    // ... MonitorAsync with current.Url / current
}
```

**为什么不是并行**：
> 一个任务的意义就是它占一个槽位。每个间隔发 N 个请求会**悄悄把负载乘以 N**。

原来那 5 处 `task.Product` 全部改成 `current`——**改的时候发现 `current` 定义在 `try` 里，
出了作用域就不在了**，得提到 `while` 体内、`try` 之前。

### 四个测试锁住形状

| 测试 | 断言 |
|---|---|
| `ASingleProductTaskStillReportsExactlyOne` | 单商品任务 `AllProducts` 长度 1，且是同一个引用 |
| `ExtraProductsComeAfterThePrimary` | 顺序是 `Product` 在前，`ExtraProducts` 按添加顺序在后 |
| `AllProductsIsNeverEmpty` | 空任务也返回 1 个元素（防除零） |
| `TheRoundRobinCoversEveryProduct` | 7 次轮询访问 `a,b,c,a,b,c,a` |

输出：

```
order: first -> second -> third
visits: a,b,c,a,b,c,a
```

### UI 还没接

`TaskEditorWindow` 仍然只有一行 `Product URL`。**字段和引擎都支持了，控件还没加。**

这一步留着是有意的：Cart tab 的多行 UI 需要动态增删行，比加一个字段复杂得多。
**先让底层能力存在，UI 可以随时接上。**

### 验证

```
dotnet test (快速)   545 通过 / 0 失败 / 2 跳过   (+4 MultiProductTaskTests)
release build        成功
store modules        PASS 61 registered
verify.ps1           VERDICT: all checks passed
```

---
