import io
p = r'D:\projects\cyber-reverse\replica\docs\XAML_BINDINGS.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## R233：`TaskCreatorMainView` 四个成员落地（缺口 76 → 70）

复刻件把它映射成 `TaskCreatorView`（`OriginalViewClassParityTests` 的 Renamed 表里三个原名都指向它）。

| 名字 | 实现 | 依据 |
|---|---|---|
| `SizeItems` | `SizePalette.Build(Settings.CustomSizes)` | 编辑器里已有的尺码梯 |
| `ProfileItems` | `Config.BillingGroups.SelectMany(g => g.Profiles)` | **profiles 挂在 Billing 组下**，不是独立文档 |
| `ProfileGroupItems` | `Config.BillingGroups` | Billing 页左栏就是 "PROFILE GROUPS" |
| `ShowCartView` | `_tabs.SelectedIndex == 1`（可写） | Setup / Cart / Advanced 三个标签 |

**一个容易走错的地方**：第一版我按 `Config.Profiles` / `Config.ProfileGroups` 写，编译直接报
"ConfigurationStore 未包含 Profiles" —— 因为**profile 根本没有独立文档**，它们属于 `BillingGroup`。
GUI 那边（Billing 页左栏叫 PROFILE GROUPS）本来就说清了这件事，是我先去猜了模型。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('doc updated')
