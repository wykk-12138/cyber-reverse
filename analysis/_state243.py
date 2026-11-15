import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 243 轮（Status.Clickable / Solver.AIStatus / CreateModel.AccountSelectionMode / AppearanceView.ResetDefaults；缺口 48 / real 36；全套 1428 绿）。

---

## 缺口 48（real 36）

```
R234 67 → R241 52 → R243 48        noise 12 不计 → real 36
```

**本轮教训（重要）**：第一版 `AppearanceView.ResetDefaults()` 用了从未被赋值的 `_appearanceServices`，
于是 `if (s is null) return;` 永远命中 —— **编译过、测试过、点了没反应**。
抓它的办法不是加测试，是**回头检查那个字段有没有赋值点**。

**剩余 real 36**：
- `Attributes.Platform` 3 —— **已知不可得**（值不在池子里，下拉点不开，R242 二次复现）
- `FilterRow` 3 / `ComboBoxEdit` 2 —— 需抽控件
- 其余零散 ~28：`AuthWindow.Logout`、`LicenseControl.Authenticate`、`ImapView.DisconnectAycd`、
  `HistoryWindow.ShowAll`、`MonitorView.OpenFilter`、`GroupGrid.DeleteGroup`、`ProxyGroupView.Draft`、
  `SettingsView.Transition`、`ActionRow.IsFirst`、`FilterInputEntry.IsFirst`、`AccountStoreEntry.IsSelected`、
  `ActionConfig.Required`、`LocalizeFormatExtension.Value2`、`LocalizeSwitchExtension.Condition` 等

**已确认是"改名不是缺口"的**：`NotificationOptions.EnableSound`（等价于已有的 `Sound`）、
`Store.ColorSupport`/`User.IsStaff`/`BrowserProfile.DisplayName`/`AycdInboxAccount.TaskCount`（复刻件里这些类不存在，能力在别处）。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
