import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 260 轮（NotificationsView.Types / MainWindow.SettingsView / StoreGroupModal.RemoveStore；缺口 39；零编译错误）。

---

## 棘轮当前值：`MaxRealGap = 39`

## A 类剩余 7 个

`SmartActionsCreator.DeleteParam` / `SmartActionsCreator.UseTemplate`（需模板来源）/
`CheckoutView.OpenTracking`（需运单来源）/ `ReleaseView.ShowGuide`（需指南视图）/
`DataView.ViewLogs` / `SmartActionsView.ViewLogs`（需日志视图）/ `AnalyticsView.OpenRelease`（**不可得**）。

## "先读那一行"的效果对比

| 轮次 | 编译错误 |
|---|---|
| R259 | 4 次（`Session`、`SignOutAsync`、`SelectedKey`…） |
| **R260** | **0 次** |

差别只在动手前确认签名。**这条规矩保留。**

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
