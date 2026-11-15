import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 261 轮（SmartActionsView.ViewLogs + ReleaseView.ShowGuide；缺口 36；不可达 29；又救活两个死窗口）。

---

## 棘轮当前值：`MaxRealGap = 36`；不可达 UI 类 **29**

## 累计救活七个"声明了但没人构造"的窗口

| 轮次 | 窗口 | 由谁构造 |
|---|---|---|
| R231 | `StoreGroupModal` | `UtilitiesView.EditStoreGroup()` |
| R232 | `NotificationView` / `UserView` | `MainWindow.OpenNotifications()` / `OpenProfile()` |
| R234 | `SmartActionsView` / `UtilitiesView` | `MonitorWindow` 三栏外壳 |
| R261 | `HistoryWindow` / `ReleaseGuideView` | `SmartActionsView.ViewLogs()` / `ReleaseView.ShowGuide()` |

**规律**：绑定表里那些 `ViewLogs` / `ShowGuide` / `Open*` 名字，就是"谁该打开它"的名单。

## 反复出现的类型错误

**把 `UserControl` 当 `Window` 用**（`.Show(owner)`）—— R250 三处、R261 一处。
正确写法：`Views.Common.ViewHostModal.Show(this, title, control)`。

## 缺口 36 的构成

A 类剩 5：`SmartActionsCreator.DeleteParam/UseTemplate`、`CheckoutView.OpenTracking`、
`DataView.ViewLogs`、`AnalyticsView.OpenRelease`（不可得）。
B 类 31：行控件/本地化扩展/不存在的模型（见 `docs/BINDING_BACKLOG.md`）。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
