import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R336：通知面板（右上铃铛）—— 三处差异，其中两处是**我多加了东西**

实机点铃铛，面板（贴右侧的浮层，非独立窗口）：

```
0 Notifications                              [Clear]
        ┌ ✕ ┐
   Nothing to see here
   Your notifications will show up here
   （grid id = NotificationsGrid）
```

| 项 | 实机 | 复刻件（改前） |
|---|---|---|
| 标题 | **`0 Notifications`**（计数 + 词） | 只有 `Notifications`，且**多一行 `Clock`** |
| 按钮 | **只有 `Clear`**（右上） | `Clear` + **`Delete`** + `Close` |
| 空态 | `Nothing to see here` + **`Your notifications will show up here`** | `"(nothing yet)"` |

### 改了什么

1. 标题改为 `_caption` = `"{count} Notifications"`；
2. **删掉 `Clock` 行与 `Delete` 按钮** —— 实机面板的完整树里都没有（保留 `Close`：复刻件这个面板是独立窗口，需要关闭手段）；
3. 空态改成两行，第二行 = `EmptyBody = "Your notifications will show up here"`。

`_clock` 字段保留（`services.Clock` 仍在用），只是不再显示。

### 教训

前几轮我一直在"补缺失"，这一轮是**删多余**。两者同等重要，而"删"更难 ——
它需要先证明"实机的树里没有"，而这次恰好拿到了完整面板树。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 336 轮：通知面板 —— 这一轮不是"补缺失"，是**删多余**

### 一、实机（点右上铃铛）

```
0 Notifications                              [Clear]
   Nothing to see here
   Your notifications will show up here
   （grid id = NotificationsGrid）
```

### 二、三处差异

| 项 | 实机 | 复刻件（改前） |
|---|---|---|
| 标题 | `0 Notifications` | `Notifications` + **多一行 `Clock`** |
| 按钮 | 只有 `Clear` | `Clear` + **`Delete`** + `Close` |
| 空态 | 两行（含 `Your notifications will show up here`） | `"(nothing yet)"` |

### 三、改动

标题改为 `"{count} Notifications"`；**删掉 `Clock` 行与 `Delete` 按钮**（完整面板树里都没有）；
空态改成实机那两行。`_clock` 字段保留（时钟仍在用），只是不显示。

### 四、这一轮的意义

前面十几轮我做的几乎都是"补缺失"。这一轮是**删多余** —— 而"删"更难：
**它需要先证明"实机的树里没有"，而不是"我没看见"。** 这次凑巧拿到了完整面板树。

### 五、验证

```
NotificationPopupTests   1 通过
完整套件                 1488 通过 / 0 失败 / 2 跳过
```
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 336 轮（通知面板：标题带计数、删掉实机没有的 `Clock`/`Delete`、空态逐字；全套 1488 绿）。

---

## 实机核对第七个面：通知面板

| 项 | 实机 | 复刻件现在 |
|---|---|---|
| 标题 | `0 Notifications` | 同（`"{count} Notifications"`） |
| 按钮 | 只有 `Clear` | `Clear` + `Close`（独立窗口需要关闭手段） |
| 空态 | `Nothing to see here` / `Your notifications will show up here` | 同 |

**删掉了** `Clock` 行与 `Delete` 按钮 —— 实机完整面板树里都没有。

## 状态

```
完整套件   1488 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     22.1 GB / 可用 15.4 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
