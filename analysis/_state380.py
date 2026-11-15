import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 380 轮：`PublishTemplateModal.Groups`（缺口 13 → 12）

对话框本来就把组名填进 `_groups`（`ListBox`），只是没暴露出来。加一个只读属性即可：

```csharp
public IReadOnlyList<string> Groups => _groups.ItemsSource?.Cast<string>().ToList() ?? new List<string>();
```

**这一轮一次编译就过** —— 因为先读了字段（`_groups` 就在第一行），也没去猜 `Config` 的路径。

```
完整套件   1538 通过 / 0 失败 / 2 跳过
bind_scope 13 → 12
```

### 这一轮的一句话

> 缺口从 52 一路降到 12，剩下的每一个都越来越"需要界面位置或真数据"。

> **下降曲线变平，说明剩下的不是难找，而是难证。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 380 轮（`PublishTemplateModal.Groups`；类型级缺口 13 → 12）。

---

## 剩余 12 个类型级缺口

`Profile.Card/Username` · `ProxyTester.Name` · `AccountGrid.*` · `GroupGrid.Items/Store` ·
`ProfileCreatorView.*` · `CloudflareSolversView.Edit` · `DataView.ViewLogs` ·
`GeneralSettingsView.ProfileItems` · `GoogleAccountsView.Edit` · `ImapView.Configure` ·
`SmartActionsView.Clock/Export` · `TaskView.Toggle`

**共同点**：都需要"界面位置"或"真实数据/服务"才能定，光看名字定不了。

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级，起点 52）
UI 类      104 声明 / 28 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
