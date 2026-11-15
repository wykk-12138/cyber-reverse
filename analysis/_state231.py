import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 231 轮（UtilitiesView 五个绑定名落地，顺手救活 StoreGroupModal；缺口 79；不可达 UI 类 36→35；1425 绿）。

---

## 缺口 79（whole-source），剩余构成

```
R225 167(per-file 高估) → 107 → 105 → 105 → 96 → 83 → 79
```

| 类型 | 缺 | 类别 |
|---|---|---|
| `Models.EditValue\\`1` | 12 | **噪音**（泛型 `HasMultiple_NN`），不计 |
| `SmartActionsCreator` | 5 | **卡在模型**（多动作 / 筛选器 Inputs / Behaviour） |
| `CreateInputModel` | 4 | 待查 |
| `TaskCreatorMainView` | 4 | 复刻件里是另一个类名，待对 |
| `Platform` | 3 | 属性 `InputType / QuantitySupport / QuantityAutoAdjustSupport` |
| `MainWindow` | 3 | `OpenMonitor / OpenNotifications / OpenProfile` |

**本轮顺手成果**：`StoreGroupModal` 从"声明了没人构造"的基线里掉了出去（36 → 35）——
补绑定的同时把死窗口接上线，两条守卫各自响了一次。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
