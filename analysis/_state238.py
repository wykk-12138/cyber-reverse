import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 238 轮（PaymentView 两个成对成员落地；缺口 63 / real 51；13 条受影响测试绿）。

---

## 缺口 63（real 51）

```
R225 167(per-file) → … → R234 67 → R236 65 → R238 63
noise 12（HasMultiple_NN / Value_NN）不计 → real 51
```

**已完成的一批（都是"界面在做、名字不在"）**：`TaskView` 30/30、`ProxyView` 6、`UtilitiesView` 5、
`MainWindow` 7、`MonitorWindow` 5、`TaskCreatorView` 4、`SmartActionsCreator` 8、`AccountGrid` 2、`PaymentView` 2。

**下一批候选**：`NotificationsView`（`SelectSound/ResetSound`，`SoundPlayer` 已有）、
`SizeCreatorView`（`SizeOptions/ToggleSizeSelected`）、`DataView`（`DataProviders/ViewBackups`）、
`CaptchaProvidersView`（`EnabledProviders/DisabledProviders`）。

**结构差异类（B2，需先抽控件）**：`ComboBoxEdit`（`ClearSelectionCommand/RemoveTokenCommand`）、
`FilterRow`（`IsFirst/Passed/ValueText`）。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
