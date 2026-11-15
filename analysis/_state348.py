import io
p = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('| `CustomStoresView` / `CustomSizesView` | `Rows` / `Delete`（R347）；`View` 语义未知，留白 |',
              '| `CustomStoresView` / `CustomSizesView` | `Rows` / `Delete`（R347）；`View` 语义未知，留白 |\n| `HistoryWindow` | `Exit` / `Minimise`（R348）；`SmartAction` / `View` 仍未知 |\n| `SmartActionsView` | `OpenCreator`（R348）；`Clock` / `Export` 仍未知 |')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('backlog updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 348 轮：`Exit` / `Minimise` / `OpenCreator` 三个语义无歧义的绑定名

### 一、判定

| 类型 | 成员 | 判定 | 处理 |
|---|---|---|---|
| `HistoryWindow` | `Exit` / `Minimise` | 关窗 / 最小化，无歧义 | **实现** |
| `HistoryWindow` | `SmartAction` / `View` | 是什么？未知 | 留白 |
| `SmartActionsView` | `OpenCreator` | 打开"新建动作" —— 私有 `OpenActionEditor(null)` 已是这条路径 | **实现**（转调） |
| `SmartActionsView` | `Clock` / `Export` | 时钟？导出成什么格式？ | 留白 |

### 二、验证

```
SmartActionWindowOpsTests   1 通过
完整套件                    1514 通过 / 0 失败 / 2 跳过
bind_scope                  HistoryWindow 4 → 2；SmartActionsView 3 → 2（类型数仍 41，成员在减少）
```

### 三、注意一个计量细节

`bind_scope.py` 数的是**类型**，不是成员。所以"两个类型各少 2 个成员"不会让 41 变小 ——
**这个口径会掩盖成员级的进展**。已在 `docs/METHOD.md` 记一笔：看类型数时也要看成员数。

### 四、这一轮的一句话

> 前几轮我盯着 41 这个数在减；这一轮它没动，因为两个类型都还在名单上。

> **指标不降不等于没进展 —— 也可能是指标的分辨率不够。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t3 = io.open(p3, encoding='utf-8').read()
add3 = '''

### §10.2 `bind_scope.py` 数的是类型，不是成员（R348）

两个类型各少 2 个成员，总数不动（41 → 41）。**看数时要同时看"类型数"和"成员数"**；
否则会把整轮的进展看成零。
'''
io.open(p3, 'w', encoding='utf-8', newline='').write(t3 + add3)
print('METHOD §10.2 added')

p4 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t4 = io.open(p4, encoding='utf-8').read()
lf = t4.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 348 轮（`HistoryWindow.Exit/Minimise` + `SmartActionsView.OpenCreator`；成员数在降，类型数仍 41）。

---

## 计量提醒（`docs/METHOD.md` §10.2）

`bind_scope.py` 数的是**类型**：两个类型各少 2 个成员时，总数**不动**。
看进展要同时看**类型数**与**成员数**。

## 已修的绑定名（累计）

`IWebhook` 六成员 · `LoginControl` 五操作 · `TaskView.ClearAll/OpenSettings` ·
`GroupSummary.StartAll/StopAll` · `HelpView.OpenUrl` · 两个自定义页 `Rows/Delete` ·
`HistoryWindow.Exit/Minimise` · `SmartActionsView.OpenCreator`

## 留白（行为未知，只记名）

`TaskView` 六个 · `SmartActionsView.Clock/Export` · `GroupSummary` 三个 ·
`HistoryWindow.SmartAction/View` · `PublishTemplateModal.Groups` · 两个自定义页的 `View`

## 状态

```
完整套件   1514 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 41（类型口径）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p4, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
