import io
p = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('| `HelpView` | `OpenUrl`（R346，本地函数 → 成员） |',
              '| `HelpView` | `OpenUrl`（R346，本地函数 → 成员） |\n| `CustomStoresView` / `CustomSizesView` | `Rows` / `Delete`（R347）；`View` 语义未知，留白 |')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('backlog updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 347 轮：两个自定义页的 `Rows` / `Delete`（`View` 继续留白）

### 一、绑定表在这两页点了同一组名字

```
Cybersole.Ui.Views.Settings.CustomStoresView -> Add, Clear, Delete, Rows, View
Cybersole.Ui.Views.Settings.CustomSizesView  -> Add, Clear, Delete, Rows, View
```

`Rows`（列表本身）与 `Delete`（按位置删一条并保存）语义清楚 → 实现；
**`View` 仍然不知道是"查看 URL"还是"打开编辑器"** → 留白，写进 backlog。

### 二、实现方式

两页原来都把数据放在构造器的局部变量里（`stores` / `sizes`）。加了
`_storeRows` / `_sizeRows` 字段 + `Rows` 属性 + `Delete(int)`，`Delete` 越界返回 false。

### 三、验证

```
CustomStoresRowsTests   2 通过
完整套件                1513 通过 / 0 失败 / 2 跳过
bind_scope              42 → 41
```

### 四、这一轮的一句话

> 这一轮做的三件事（`Rows`、`Delete`、留白 `View`）里，**最难的是第三件** ——
> 它没有任何产出，只是诚实地承认"我不知道 `View` 是什么"。

> **留白也是一种交付物，只要它被写下来了。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 347 轮（`CustomStoresView` / `CustomSizesView` 补 `Rows` / `Delete`；`View` 留白；类型级缺口 41）。

---

## 类型级缺口修到 41（起点 52）

| 类型 | 轮次 | 修了什么 |
|---|---|---|
| `IWebhook` | R342 | 六成员补齐 |
| `LoginControl` | R343 | 五个操作提为成员 |
| `TaskView` | R344 | `ClearAll` / `OpenSettings` |
| `GroupSummary` | R345 | `StartAll` / `StopAll` |
| `HelpView` | R346 | `OpenUrl` |
| `CustomStoresView` / `CustomSizesView` | R347 | `Rows` / `Delete` |

**留白清单**（行为未知，只记名）：两个自定义页的 `View`、`TaskView` 六个、`SmartActionsView` 三个、
`GroupSummary` 三个、`HistoryWindow` 四个、`PublishTemplateModal` 一个。

## 状态

```
完整套件        1513 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      41（筛查器口径）
mutation        29 / 29 fired
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
