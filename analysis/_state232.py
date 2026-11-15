import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 232 轮（主壳 7 个绑定名落地，又救活 NotificationView / UserView；缺口 76；不可达 33；1428 绿）。

---

## 缺口 76（whole-source）

```
R225 167(per-file 高估) → 107 → 105 → 105 → 96 → 83 → 79 → 76
```

| 类型 | 缺 | 类别 |
|---|---|---|
| `Models.EditValue\\`1` | 12 | **噪音**，不计 |
| `SmartActionsCreator` | 5 | 卡在模型（多动作 / Inputs / Behaviour） |
| `CreateInputModel` | 4 | 待查 |
| `TaskCreatorMainView` | 4 | 复刻件里是另一个类名 |
| `Attributes.Platform` | 3 | `InputType / QuantitySupport / QuantityAutoAdjustSupport` |
| `SmartActionsView` | 3 | `Clock / Export / OpenCreator`？ 待核 |

## 被绑定点亮的三扇门（R231-R232）

| 窗口 | 之前 | 现在 |
|---|---|---|
| `StoreGroupModal` | 声明未构造 | `UtilitiesView.EditStoreGroup()` |
| `NotificationView` | 声明未构造 | `MainWindow.OpenNotifications()` |
| `UserView` | 声明未构造 | `MainWindow.OpenProfile()` |

不可达 UI 类 **36 → 33**。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
