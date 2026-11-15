import io
p = r'D:\projects\cyber-reverse\replica\docs\XAML_BINDINGS.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## R231：`UtilitiesView` 五个绑定名落地（`StoreGroupModal` 因此从"不可达"变成可达）

| 名字 | 实现 |
|---|---|
| `StoreGroups` | `Config.Settings.StoreGroups` |
| `CreateStoreGroup(name)` | 建组（名字为空则 "Group N"），保存并刷新 |
| `CloneStoreGroup()` | 复制选中组（含 stores 列表） |
| `DeleteStoreGroup()` | 删除选中组 |
| `EditStoreGroup()` | 打开 `StoreGroupModal` —— **这个窗口此前从未被构造过**，于是它从"声明了没人用"的基线里掉了出去（36 → 35） |

三个按钮（New / Clone / Delete）改为调用这三个命令，行为只有一份。

> 这条值得单独记：**给一个命令补名字，顺手把一个"死窗口"救活了** —— 两条守卫各自响了一次。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('doc updated')
