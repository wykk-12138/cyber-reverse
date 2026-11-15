import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 229 轮（TaskView 的 30 个绑定名全部到位：缺 8 → 缺 0；缺口 105→96；1425 绿）。

---

## XAML 绑定缺口进度（whole-source 口径）

```
819 成员 / 174 类型
R225: 167（per-file 口径，高估）
R226: 107     R227: 105     R228: 105（CopyUrl 恢复）    R229: 96
```

**剩余 96 的构成**：
- `SmartActionsCreator` 11（编辑器命令集，尚未成体系）
- `Models.CreateInputModel` 4、`TaskCreatorMainView` 4、`UtilitiesView` 4
- `Models.EditValue\\`1` 12 —— **泛型噪音，不计**

**TaskView 已完成 30/30**，做法是"一处实现两个入口"：`TaskGrid` 的 9 个私有钩子配了命名入口，
`TaskView` 暴露原版绑定名；`StopAll` 按钮与右键菜单现在走同一个方法。

**一处已知差异（写在代码里）**：`EditAll` 与 `EditSelected` 共用入口 —— 复刻件的编辑器只接受单个 `BotTask`。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
