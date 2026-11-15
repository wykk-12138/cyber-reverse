import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 259 轮（A 类清掉 5 个：GroupGrid.DeleteGroup / UserView.LogOut / CreateGroupModal.Types / 两个 Creating；缺口 41）。

---

## 棘轮当前值：`MaxRealGap = 41`

## 按账本推进（`docs/BINDING_BACKLOG.md`）

A 类 15 个里已做 5 个；剩 10 个：`SmartActionsCreator.DeleteParam/UseTemplate`、`CheckoutView.OpenTracking`、
`ReleaseView.ShowGuide`、`MainWindow.SettingsView`、`DataView.ViewLogs`、`SmartActionsView.ViewLogs`、
`NotificationsView.Types`、`StoreGroupModal.RemoveStore`、`AnalyticsView.OpenRelease`（**不可得**）。

## 反复出现的错误类型（本轮 4 次）

"没先读代码就动手"：`AppServices.Session`（应为 `Auth`）、`AuthService.SignOutAsync`（应为同步 `SignOut`）、
`GroupGrid.SelectedKey`（该属性不存在，得自己记住）。

**新规矩**：动手前**先读那一行**（字段/方法签名），别按"应该是这样"写。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
