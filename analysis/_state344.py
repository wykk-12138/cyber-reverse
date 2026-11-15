import io
p = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## 类型级缺口（R342 起）：绑定表要的成员没长在它该在的类型上

名字级缺口只能回答"这个名字在整个仓库里出现过"。`tools/bind_scope.py` 按**类型自己的块**（花括号配对 +
基类上溯）再问一遍，两者差得很远。**它是筛查器，不是判决书**：框架/继承成员会误报，每条都要手工读一遍。

### 已修

| 类型 | 轮次 | 修了什么 |
|---|---|---|
| `IWebhook` | R342 | 补齐 `Enabled / Events / ExtraFields / Name / Type / Url` 六成员 |
| `LoginControl` | R343 | `Cancel` / `OpenBrowser` / `SignUp` / `UseCode` / `SignInAsync` 从匿名回调提成成员 |
| `TaskView` | R344 | `ClearAll`（原 `ClearTasks`）、`OpenSettings` |

### 绑定表点名、但**行为尚未恢复**的（不猜，先记）

| 类型 | 成员 | 情况 |
|---|---|---|
| `TaskView` | `CreateGroup` `LinkChange` `MoveGroup` `PinGroups` `Quicktask` `Toggle` | 绑定表有名字，**不知道具体做什么**；快捷键页给了一部分线索（`Ctrl+M` Link Change、`Ctrl+Q` Quicktask、`Ctrl+G` New Group） |
| `SmartActionsView` | `Clock` `Export` `OpenCreator` | 同上 |
| `GroupSummary` | `Clone` `Delete` `Edit` `StartAll` `StopAll` | 组摘要行上的五个操作，行为清楚但未落到该类型 |
| `HistoryWindow` | `Exit` `Minimise` `SmartAction` `View` | — |
| `PublishTemplateModal` | `Groups` | — |

> 纪律：**"绑定表有名字"不等于"我知道它做什么"**。名字先记进来，行为等反编译或 GUI 证据到位再落。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('BINDING_BACKLOG: type-scoped section added')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 344 轮：`TaskView` 八缺其二补齐，剩下六个**记名不猜行为**

### 一、绑定表在这一个类型上点了 30 个名字

```
ClearAll, CloneSelected, CopyUrl, CreateGroup, Delete, DeleteSelected, Edit, EditAll, EditSelected,
ForceStartSelected, LinkChange, MoveGroup, NextGroup, OpenBrowser, OpenGroupPopup, OpenSettings,
OpenSolvers, OpenStaggerStart, OpenTaskCreator, OpenTaskView, PinGroups, PreviousGroup, Quicktask,
Search, SetQuery, StartAll, StartSelected, StopAll, StopSelected, Toggle
```

复刻件里 `ClearTasks` / `OpenEditor` / `CycleGroup` … 覆盖了大部分，但**名字对不上**。

### 二、这一轮补了两个能确定的

- `ClearAll()` → 转调 `ClearTasks()`（按钮本来就写 "Clear Tasks"）
- `OpenSettings()` → 导航到 Settings（与 `ProxyView.OpenSettings` 同一手法）

`bind_scope.py`：`TaskView` 从缺 8 降到缺 6。

### 三、剩下六个：**记名，不猜行为**

`CreateGroup` `LinkChange` `MoveGroup` `PinGroups` `Quicktask` `Toggle` —— 绑定表有名字，
但**行为未知**。给它们编一个"看起来很合理"的实现，就是又一次 R259/R302 的错。

已写进 `docs/BINDING_BACKLOG.md` 的"绑定表点名但行为未恢复"表（含 `SmartActionsView`、`GroupSummary`、
`HistoryWindow` 等）。

> **"绑定表有名字" ≠ "我知道它做什么"。**

### 四、验证

```
完整套件   1507 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 上一轮我学会了"工具给出数字先问它稳不稳"；这一轮学会**"名字给出方向，但名字不是行为"**。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 344 轮（`TaskView` 补 `ClearAll`/`OpenSettings`；六个未知行为**记名不猜**）。

---

## 类型级缺口的处理原则（R344 定下）

| 情况 | 做法 |
|---|---|
| 行为已存在、只是名字不同 | **提成绑定名**（R343 `LoginControl`、R344 `TaskView.ClearAll`） |
| 行为清楚、尚未落到该类型 | 照绑定名实现（如 `OpenSettings` 导航） |
| **行为未知** | **只记名**，写进 `docs/BINDING_BACKLOG.md`，不编实现 |

当前"记名未落"的：`TaskView` 六个（`CreateGroup` `LinkChange` `MoveGroup` `PinGroups` `Quicktask` `Toggle`）、
`SmartActionsView` 三个、`GroupSummary` 五个、`HistoryWindow` 四个、`PublishTemplateModal` 一个。

## 状态

```
完整套件        1507 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      44（筛查器口径，含框架成员误报）
mutation        29 / 29 fired
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
