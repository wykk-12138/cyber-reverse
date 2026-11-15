import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 234 轮（Monitor 窗口改成三栏外壳，救活 SmartActionsView / UtilitiesView；缺口 67；不可达 31；**建议重启**）。

---

## ⚠ 机器状态：请重启

```
Commit 32.0 / 65.71 GB（超过自定 30 GB 线）   可用物理 10.11 GB
purge 需要管理员权限，本轮被拒（ABORT: SeProfileSingleProcessPrivilege）
```

**重启后第一件事**：跑一次完整套件（本轮只跑了 21 条守门测试，全套 1430 条未跑）。

## Monitor 窗口是三栏外壳（R234）

原版在 `MonitorWindow` 上绑定 `ShowMonitor / ShowSmartActions / ShowUtilities` —— **一个只有请求流的窗口绑不出这三个**。
已改为 `TabControl` 三页：Monitor（请求流）/ Smart Actions（`SmartActionsView`）/ Utilities（`UtilitiesView`）。

**五轮共救活五个从未被构造的窗口**：`StoreGroupModal`、`NotificationView`、`UserView`、
`SmartActionsView`、`UtilitiesView`。不可达 UI 类 **36 → 31**。

## 缺口 67

```
R225 167(per-file) → 107 → 105 → 105 → 96 → 83 → 79 → 76 → 70 → 67
```

| 类型 | 缺 |
|---|---|
| `Models.EditValue\\`1` | 12（噪音，不计） |
| `SmartActionsCreator` | 5（卡在模型） |
| `CreateInputModel` | 4 |
| `Attributes.Platform` | 3（缺每平台能力值证据） |

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
