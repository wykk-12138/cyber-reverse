import io
p = r'D:\projects\cyber-reverse\replica\docs\XAML_BINDINGS.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## R230：`SmartActionsCreator` 补了 8 个，剩 5 个**卡在模型上**

补上（都有模型支撑、按钮真的走它们）：

| 名字 | 实现 |
|---|---|
| `Save` | 原本就是 `private`，改成对外 |
| `IsEditing` | `existing is not null` |
| `SmartAction` | 正在编辑的动作 |
| `AddFilter(filter)` | 加筛选器 + 重画第 2 步（按钮改为调用它） |
| `DeleteFilter(index)` | 删除并同步 `SmartAction.Filters`（按钮改为调用它） |
| `Clone()` | 复制动作（含筛选器）写进文档并保存 |
| `Minimise()` / `Exit()` / `CloseOverlay()` | 宿主窗口操作 |

**卡在模型上的 5 个（需要先改模型，不是加个名字就行）**：

| 名字 | 缺什么 |
|---|---|
| `AddAction` / `DeleteAction` | 复刻件的 `SmartAction` 是**单个动作**（`Kind`/`Target`），原版有 `Actions` 集合与 `ActionParams`/`ActionConfig` 类型 |
| `AddInput` / `DeleteInput` / `DeleteParam` | 原版筛选器带 `Inputs`（`FilterInputEntry`），复刻件的 `SmartActionFilter` 只有 Field/Operator/Value |
| `ToggleFilterBehaviour` | 原版筛选器有 `Behaviour`（AND/OR），复刻件没有这个字段 |

这些**不是命名差异**，是**模型少了东西**。要做就得先扩模型（并补对应的序列化测试），
所以它们进的是"待扩展模型"清单，而不是"待加名字"清单。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('XAML_BINDINGS.md updated')
