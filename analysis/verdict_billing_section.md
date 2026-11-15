### `Billing` 页：六个按钮全真，但有一条走错了组

### 六个 handler 都是真的

```csharp
UiKit.Button("New", ...)      // 加组 + 保存 + 刷新
UiKit.Button("Clone", ...)    // 深拷贝组（含每个 profile）
UiKit.Button("Delete", ...)   // 删组 + 保底建一个空组
UiKit.Button("Add", ...)      // 打开 ProfileEditorWindow
UiKit.Button("Clone", ...)    // 复制选中的 profile
UiKit.Button("Delete", ...)   // 删选中的 profile
```

**没有一个是 `Status("...")`。** 和 `Proxies` 一样，这一页没有死按钮。

### 但实测发现一个走错组的 bug

**操作**：选中 `VIP`，点 `Add`，填名字邮箱，保存。

**结果**：

```
+ [21] ListItem "Group 1  (1 profile(s))"
- [20] ListItem "Group 1  (0 profile(s))"
   VIP  (0 profile(s))   ← 没变
```

**profile 落进了 `Group 1`，不是选中的 `VIP`。**

### 原因

`ProfileEditorWindow.Submit()`：

```csharp
var group = _services.Config.BillingGroups.FirstOrDefault();
```

**永远是第一个组。** 用户选中哪个组，编辑器不知道——`BillingView` 打开它时没传：

```csharp
var editor = new ProfileEditorWindow(_services);
```

### 修

**编辑器接受一个可选的组**：

```csharp
public ProfileEditorWindow(AppServices services, Profile? existing = null,
                           BillingGroup? group = null)
{
    _services = services;
    _group = group;
    ...
}

private void Submit(Profile? existing)
{
    var group = _group ?? _services.Config.BillingGroups.FirstOrDefault();
    ...
}
```

**调用方传选中的组**：

```csharp
UiKit.Button("Add", () =>
{
    var group = Selected();
    if (group is null) return;

    // pass the selected group: without it the editor fell back to BillingGroups[0]
    // and a profile added while another group was selected landed in the wrong one
    var editor = new ProfileEditorWindow(_services, null, group);
    editor.Closed += (_, _) => Refresh();
    _ = editor.ShowDialog(...);
}),
```

### 修好后重测

选中 `VIP` → `Add` → 填 → `Save`：

```
+ [20] ListItem "VIP  (1 profile(s))"
- [44] ListItem "VIP  (0 profile(s))"
```

**进对了。**

### 这个 bug 的形状和 R98 的 `ExtraProducts` 一样

| 轮次 | 症状 | 原因 |
|---|---|---|
| R98 | 编辑任务时 `ExtraProducts` 不回填，保存后清空 | 构造时没读 `existing` |
| **R107** | **加 profile 时进了第一个组，不是选中的组** | **打开窗口时没传选中的组** |

**都是「上下文没传进去，窗口自己猜了个默认值」。**

而两次都只有**真的操作一遍**才能发现——`FirstOrDefault()` 看起来无害，
它只在「有第二个组且用户选了它」的时候错。

### `Billing` 页的判据

| 检查 | 结果 |
|---|---|
| 六个按钮有真实实现 | ✅ |
| `New` 真的加组 | ✅ 实测 `VIP (0 profile(s))` 出现 |
| `Add` 打开编辑器 | ✅ 窗口 `New profile` 出现，16 个字段 |
| `Add` 放进正确的组 | ❌ → 已修 |
| `Save` 落盘 | ✅ `billing.json` 里能看到 |

**结构对，语义错。** 这是第三类缺陷——比死按钮隐蔽，因为每一步都有可见反馈。

### 清理

测试产生的 `VIP` 组和两个 profile 已从 `billing.json` 删掉，回到 `[('Group 1', 0)]`。

### 验证

```
dotnet test      549 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
billing.json     back to one empty group
```

---
