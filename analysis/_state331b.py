import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 331 轮（Tasks 页实机对照：**零差异**；两页 GUI 交叉验证完成）。

---

## 已用实机验证的两页（`docs/GUI_BASELINE.md`）

| 页 | 结论 |
|---|---|
| Settings 导航 + General + Payment | 结构与文案全一致；`Max Open` 是**条件行**（R330 结掉 R77 悬案） |
| Tasks | **零差异**：分组下拉+`...`、四色药丸（含色值顺序）、列头五列、`0 Tasks`、六键 3+3、空态两行 |

原版仍在运行（pid 14248）。

## 本轮自纠

先查 `TaskGrid.cs` 找四色药丸 → 没找到 → 差点记成"缺"；
实际在 `TaskView.cs:301-304`（`TaskGrid` 只管列表行）。**第三次"未命中先复核查法"。**

## 状态

```
完整套件   1480 通过 / 0 失败 / 2 跳过（R330）
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.3 GB / 可用 17.9 GB
```

## 下一步候选（原版还开着）

Proxies / Accounts / Billing / Home 四页的实机对照；`AccountStoreEntry.IsSelected` 的选中态表现值得一看。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
