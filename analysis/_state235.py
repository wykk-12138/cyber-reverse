import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 235 轮（只做证据整理：67 个缺口分成 12 噪音 / 30 接线 / 12 卡模型；工具新增 `--buckets`；未编译未测试）。

---

## ⚠ 机器状态：请重启（未重启）

```
Commit 30.77 GB（自定线 30 GB）   可用物理 11.4 GB   开机仍是 17:29:48
purge 需要管理员权限，被拒
```

**重启后第一件事**：跑完整套件（1430 条；R234/R235 两轮都没跑全套）。本轮**故意没编译没测试**。

## 缺口 67 = 12 噪音 + 30 接线 + 12 卡模型

`python tools\\bind_diff.py --buckets`：

```
missing: 67     noise (HasMultiple_NN / Value_NN): 12     real gap: 55
```

| 类 | 数量 | 例子 |
|---|---|---|
| A 噪音 | 12 | `EditValue\\`1.HasMultiple_NN` / `Value_NN` |
| B 照名字接线 | 30 | `AccountGrid.CopyAccounts/CopyPassword`、`ComboBoxEdit.ClearSelectionCommand`、Settings 各页成对成员 |
| C 卡在模型 | 12 | `SmartActionsCreator` 5 / `Attributes.Platform` 3 / `CreateInputModel` 4 |

完整清单在 `docs/XAML_BINDINGS.md` 的「R235 权威 backlog」一节。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
