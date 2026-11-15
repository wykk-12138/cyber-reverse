import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 236 轮（AccountGrid 两个绑定名接线；缺口 65 / real 53；内存纪律改为"看可用物理"）。

---

## 内存纪律（R236 修订）

| 指标 | 旧 | 新 |
|---|---|---|
| Commit | ≥ 30 GB 就停 | **软线**：高不危险，可继续做小步 |
| 可用物理 | — | **硬线**：< 8 GB 停手 |
| Repurposed | ≥ 2.5 GB 停 | 保留 |

理由：Commit 是账本不是占用；本轮在 Commit 30.85→32.26 GB、可用 11.3→9.84 GB 的情况下完成了小步工作。

**仍然欠着**：完整套件（1430 条，R234/R235/R236 三轮都没跑全套）。

## B 类还要再分一层

| 子类 | 例子 | 做法 |
|---|---|---|
| B1 行为在别处 | `AccountGrid.CopyAccounts/CopyPassword`（R236 完成） | 加公开命令委托同一实现 |
| B2 控件结构不同 | `ComboBoxEdit`、`FilterRow`、Settings 各页成对成员 | 抽控件，或记为结构差异 |

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
