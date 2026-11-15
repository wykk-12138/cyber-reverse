import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 239 轮（NotificationsView 声音 2 + SizeCreatorView 尺码 3；缺口 59 / real 47；20 条受影响测试绿）。

---

## 缺口 59（real 47）

```
R234 67 → R236 65 → R238 63 → R239 59      noise 12 不计 → real 47
```

**已完成批次**：TaskView 30/30、ProxyView 6、UtilitiesView 5、MainWindow 7、MonitorWindow 5、
TaskCreatorView 4、SmartActionsCreator 8、AccountGrid 2、PaymentView 2、NotificationsView 2、SizeCreatorView 3。

**下一批候选**：`DataView`（`DataProviders/ViewBackups`）、`CaptchaProvidersView`（`EnabledProviders/DisabledProviders`）、
`CreateInputModel`（4，需先看模型）、`FilterRow`（3，需先抽控件）。

## 两条被"命名"逼出来的语义（R239）

- `ResetSound` = **设成空路径（平台默认音）**，不是删字段 —— 空值表达"默认"是原版的做法。
- `ToggleSizeSelected` 返回 `bool`（加了 / 删了），因为"切换"有两种结果。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
