import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 250 轮（ProfileView 六个绑定名落地；真实缺口 96 → 80；两套实现一致；89 条受影响测试绿）。

---

## 棘轮当前值：`MaxRealGap = 80`（C# 与 python 都给 80）

## 已关闭（按真实度量）

`ProfileView` 六个：`CreateGroup / OpenCsvEditor / OpenCreator / OpenSettings / CreateTest / MoveGroup`。
其中 **`OpenSettings()` 调用 `MainWindow.Navigate("Settings")`** —— R232 补的命令第一次有调用者。

## 真实 backlog 头部（80 剩余）

| 类型 | 缺 |
|---|---|
| `SmartActionsCreator` | 7 |
| `ProxyView` | 5（CreateGroup/MoveGroup/OpenSettings/ProxyTesters/TestAllKeybind） |
| `MessageBoxDialog` / `ProfileCreatorView` | 各 4 |
| `FilterRow` / `ProfileCsvRow` / `Platform` / `TaskView` / `AccountGrid` / `AnalyticsView` | 各 2–3 |
| 其余若干 | 各 1–2 |

## 反复出现的"我以为"（三次编译错误，R238 起第 6 次）

`ProfileGenerator` 不存在（应为 `ExpressionEngine`）、`SelectedProfiles()`/`MoveToGroup()` 不存在
（应为 `BillingGroup.Profiles` 下标操作）、`PaymentView._services` 不存在。
**都是编译器能抓的便宜错误**；真正的风险是编译通过但语义错的地方。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
