import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 379 轮：`HistoryWindow.SmartAction` / `View`（缺口 14 → 13）

### 一、证据

locale 里有一条 `HistoryWindow.LogsFormat` = **"{0} - Logs"** —— 一个标题模板，说明这个窗口的标题是
"<某物> - Logs"。配合绑定表的 `SmartAction` / `View` 两个成员，最合理的解释：

- `SmartAction`：这个窗口在看哪个动作的历史（null = 全部）；
- `View`：显示的是 "History" 还是 "Logs"。

### 二、实现

两个都是**可写属性**，设置后重新渲染（`Render()`），`SmartAction` 同时按
`string.Format(LocaleLogsFormat, …)` 改标题；模板字符串作为 `public const string LocaleLogsFormat` 暴露，
测试可以直接对着它断言。

### 三、一次小失误

我写 `Refresh()`，类里没有 —— 实际叫 `Render()`。**第 N 次"以为有这个方法"。**

```
完整套件   1538 通过 / 0 失败 / 2 跳过
bind_scope 14 → 13
```

### 四、这一轮的一句话

> 标题模板也是证据：它告诉我这个窗口"按某个东西命名"，于是我不用猜就知道 `SmartAction` 是那"某个东西"。

> **locale 里的格式串，往往比字段名更能说明一个属性的作用。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 379 轮（`HistoryWindow.SmartAction/View`；类型级缺口 14 → 13）。

---

## 剩余 13 个类型级缺口

`Profile.Card/Username` · `ProxyTester.Name` · `AccountGrid.*` · `GroupGrid.*` ·
`ProfileCreatorView.*` · `CloudflareSolversView.Edit` · `DataView.ViewLogs` ·
`GeneralSettingsView.ProfileItems` · `GoogleAccountsView.Edit` · `ImapView.Configure` ·
`PublishTemplateModal.Groups` · `SmartActionsView.Clock/Export` · `TaskView.Toggle`

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 13（类型级）
UI 类      104 声明 / 28 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
