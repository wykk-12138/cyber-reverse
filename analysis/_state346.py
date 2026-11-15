import io
p = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('| `TaskView` | `ClearAll`（原 `ClearTasks`）、`OpenSettings` |',
              '| `TaskView` | `ClearAll`（原 `ClearTasks`）、`OpenSettings` |\n| `GroupSummary` | `StartAll` / `StopAll`（R345） |\n| `HelpView` | `OpenUrl`（R346，本地函数 → 成员） |')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('backlog updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 346 轮：`HelpView.OpenUrl` —— 把本地函数提成绑定名，并清掉提完之后留下的死代码

### 一、绑定表要什么

`Cybersole.Ui.Views.Settings.HelpView -> OpenUrl`（只有一个成员）。

复刻件里这事由构造器内的**本地函数** `void Open(string url)` 完成 —— 行为在，名字不在。

### 二、改法

`public static bool OpenUrl(string url)`：成功返回 true、失败返回 false（无默认浏览器时不该从点击回调里抛）；
本地函数改为一行转调。**然后把转调后变成死代码的 `OpenLegacy` 删掉** —— 提名字不该留下两套实现。

### 三、验证

```
HelpViewTests   2 通过（两个链接是 https；打开不了的东西返回 false 而不是抛）
完整套件        1511 通过 / 0 失败 / 2 跳过
bind_scope      HelpView 已从名单消失（44 → 43）
```

### 四、这一轮的一句话

> 提名字最容易被忽略的一步是**收尾**：把旧实现删掉。留着它，下一个读代码的人会以为有两条路径。

> **重构的完成标志不是"新的能跑"，是"旧的已经不在"。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 346 轮（`HelpView.OpenUrl` 提为成员并删除旧本地函数；类型级缺口 44 → 43）。

---

## 类型级缺口：已修三个类型（R343–R346）

| 类型 | 修了什么 |
|---|---|
| `LoginControl` | `Cancel` / `OpenBrowser` / `SignUp` / `UseCode` / `SignInAsync` |
| `TaskView` | `ClearAll` / `OpenSettings` |
| `GroupSummary` | `StartAll` / `StopAll` |
| `HelpView` | `OpenUrl`（并删掉被取代的本地函数） |

剩余 43 条筛查器命中里，真缺口与框架误报混在一起；每条按三档处理：
**提名字 / 照名实现 / 只记名**。

## 状态

```
完整套件        1511 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      43（筛查器口径）
mutation        29 / 29 fired
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
