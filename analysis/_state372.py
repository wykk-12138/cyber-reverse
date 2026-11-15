import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 372 轮：`LinkChange` + `Quicktask` —— 两个"从剪贴板来"的动作，靠 locale 定死

### 一、证据（全部来自池子的 locale 真值）

```
Tasks.LinkChange.InvalidTitle   = "Invalid URL"
Tasks.LinkChange.InvalidMessage = "The value retrieved from clipboard is not a valid URL."
Tasks.Quicktask.InvalidTitle    = "Invalid Quicktask"
Tasks.Quicktask.InvalidMessage  = "The value retrieved from clipboard is not a valid Quicktask format."
Monitor.LinkChange              = "Link Change"
Monitor.LaunchQuicktask         = "Launch Quicktask"
```

**"The value retrieved from clipboard"** 这一句把两个动作的输入源说死了：**读剪贴板**。

### 二、实现

| 成员 | 行为 |
|---|---|
| `LinkChange()` | 读剪贴板 → 不是 http/https 绝对 URL 就返回 `"Invalid URL\\n…not a valid URL."`；是则把选中任务的链接换掉 |
| `Quicktask()` | 读剪贴板 → 按行解析 `store \\| url`，任一行不合格式即返回 `"Invalid Quicktask\\n…not a valid Quicktask format."`；否则按行建任务 |

`Clipboard` 是**可注入的 `Func<string?>`**；没有注入时通过本视图的 `TopLevel` 读真实剪贴板。

### 三、四次编译失败（同一个病根，第 N 次）

1. `BotTask` **没有** `Url`（我把它当成有）；
2. `TaskEngine` **没有** `Add`；
3. `IClassicDesktopStyleApplicationLifetime` 没有 using；
4. 属性初始化器里写了 `this`（`CS0027`）。

每次都是"我以为它有"。**§12.2 又要加强了：连模型字段和引擎方法也要先读。**

### 四、验证

```
TaskClipboardActionTests   9 通过（含 4 条失败文案逐字断言）
完整套件                   1534 通过 / 0 失败 / 2 跳过
bind_scope                 TaskView 缺口 5 → 3（CreateGroup / MoveGroup / Toggle）
```
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 372 轮（`TaskView.LinkChange` / `Quicktask`：读剪贴板 + 原件失败文案；缺口 5 → 3）。

---

## `TaskView` 剩余 3 个无定论

`CreateGroup` · `MoveGroup` · `Toggle`

## 这一轮学到的（第 N 次同一个病）

`BotTask` 没有 `Url`、`TaskEngine` 没有 `Add`、属性初始化器里不能写 `this` ——
**先读模型字段与引擎方法，再写调用**（`docs/METHOD.md` §12.2 的延伸）。

## 状态

```
完整套件   1534 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 17（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
