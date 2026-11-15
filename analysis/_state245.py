import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 245 轮（HistoryWindow.ShowAll + ImapView.DisconnectAycd；缺口 46 / real 34；18 条受影响测试绿含死字段守卫）。

---

## 缺口 46（real 34）

```
R243 48 → R245 46        noise 12 不计 → real 34
```

**R244 的守卫已生效**：本轮两个新字段都在构造函数赋值，跑守卫无死字段 —— 同类错误没有再出现。

**剩余 real 34**：
- `Attributes.Platform` 3 —— **已知不可得**（R242 结论：值不在池子、下拉点不开）
- `FilterRow` 3 / `ComboBoxEdit` 2 —— 需抽控件
- 零散 ~26：`AuthWindow.Logout`、`LicenseControl.Authenticate`、`MonitorView.OpenFilter`、
  `GroupGrid.DeleteGroup`、`ProxyGroupView.Draft`、`SettingsView.Transition`、`ActionRow.IsFirst`、
  `FilterInputEntry.IsFirst`、`AccountStoreEntry.IsSelected`、`ActionConfig.Required`、
  `LocalizeFormatExtension.Value2`、`LocalizeSwitchExtension.Condition` 等

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
