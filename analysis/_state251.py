import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 251 轮（ProxyView 五个绑定名落地；真实缺口 78，两套实现一致；全套 1432 绿）。

---

## 棘轮当前值：`MaxRealGap = 78`

## 纪律（R251 新增）：数字必须与树同时快照

本轮补了 5 个但棘轮只掉 2，追查后发现**上一轮报的 80 是改代码之前的快照**。
→ **改完代码后不要引用改之前的数字**；要么重新测，要么等下一次测。

## 已关闭批次（真实度量）

`TaskView` 30/30、`ProxyView` 17/17、`ProfileView` 6/6、`UtilitiesView` 5/5、`MainWindow` 7/7、
`MonitorWindow` 5/5、`TaskCreatorView` 4/4、`SmartActionsCreator` 8/19、`AccountGrid` 2/2、
`PaymentView` 2/2、`NotificationsView` 2/2、`SizeCreatorView` 3/6、`CaptchaProvidersView` 2/6、
`DataView` 2/7、`SettingsViews` 若干。

## 剩余 78 的头部

| 类型 | 缺 |
|---|---|
| `SmartActionsCreator` | 7 |
| `MessageBoxDialog` / `ProfileCreatorView` | 各 4 |
| `FilterRow` / `ProfileCsvRow` / `Platform` / `AccountGrid` / `AnalyticsView` | 各 2–3 |
| 其余 | 各 1–2 |

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
