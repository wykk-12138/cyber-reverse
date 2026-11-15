import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 233 轮（TaskCreatorView 四个成员落地：profiles 挂在 BillingGroup 下，不是独立文档；缺口 70；1428 绿）。

---

## 缺口 70（whole-source），剩余构成

```
R225 167(per-file) → 107 → 105 → 105 → 96 → 83 → 79 → 76 → 70
```

| 类型 | 缺 | 类别 / 备注 |
|---|---|---|
| `Models.EditValue\\`1` | 12 | **噪音**（泛型 `HasMultiple_NN`），不计 |
| `SmartActionsCreator` | 5 | 卡在模型（多动作 / Inputs / Behaviour） |
| `CreateInputModel` | 4 | 待查（`MaxPrice/Minus/PriceCheckVisible/TogglePriceCheck`） |
| `Attributes.Platform` | 3 | `InputType/QuantitySupport/QuantityAutoAdjustSupport` —— 需要每平台的能力值，缺证据 |
| `MonitorWindow` | 3 | `ShowMonitor/ShowSmartActions/ShowUtilities` |
| 其他零散 | ~43 | 见 `python tools\\bind_diff.py` |

**易走错的点**：profile **没有独立文档**，在 `Config.BillingGroups[].Profiles` 里；Billing 页左栏标题就是
"PROFILE GROUPS"。先读界面，再猜模型。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
