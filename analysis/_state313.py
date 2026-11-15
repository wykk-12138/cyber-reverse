import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 313 轮：第 2 件控件的设计稿（`ProfileCsvRow`），不编译

### 一、原版有什么

```
ProfileCsvEditorView -> Apply, Close, ColumnChoices, GroupName, ProfileCount   （复刻件全有）
ProfileCsvRow        -> FullySelected, Number, RowError, RowStatus             （复刻件没有）
```

四个成员正好说清"一行要带什么"：行号、是否全列映射、状态文本、错误。

### 二、复刻件现状

`ProfileCsvEditorView` 有 `Parse(csv)` / `ProfileCount` / `ColumnChoices`，但解析结果只是 `string[]` 列表 ——
**没有行对象、没有行号、没有逐行状态/错误**。所以"第 2 行缺 address 2"这种信息现在表达不出来。

### 三、设计稿写了什么（`docs/CONTROL_DESIGN_ProfileCsvRow.md`）

- 行对象的骨架 + **可测可解释的判定规则**（`FullySelected` = 每列都有非空单元格；
  `RowError` 优先级：空行 → 列数不符 → 缺必需列）；
- **接到真实用处**：`ProfileCsvEditorView.Rows`，让状态区能显示"3 行就绪 / 1 行有问题（第 2 行：…）"；
- 这个视图**是会被构造的**（`ProfileView.OpenCsvEditor`），所以新行类型不会进"未构造"基线；
- 5 条验收 + 测试计划；
- **一处诚实修正**：`Number` 目前并不在缺口清单里，所以实测应该是 **29 → 26**，不是 29 → 25 ——
  并且写明"以 `backlog_report.py` 实测为准"。

### 四、这一轮为什么只写设计

可用内存 5.98 GB（远低于硬线）。上一轮"设计稿→落地"验证了这套做法的准确度（预测 29，实测 29），
所以这轮继续用同一种方式推进下一件。

### 五、这一轮的一句话

> 设计稿里我特意写下"预测 29 → 26，但以实测为准" —— **因为上一次我差点把 `Number` 也算进缺口**。

> **预测要写，但不能当结果；两者差一个数的时候，差的往往是"我漏看了清单"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 313 轮（第 2 件控件 `ProfileCsvRow` 设计稿：`docs/CONTROL_DESIGN_ProfileCsvRow.md`；未编译）。

---

## 下一个可执行任务

`docs/CONTROL_DESIGN_ProfileCsvRow.md`：

- 行对象：`Number` / `FullySelected` / `RowStatus` / `RowError`，判定规则可测可解释；
- 接到 `ProfileCsvEditorView.Rows`（该视图**会被构造**，不会进未构造基线）；
- 5 条验收 + 测试计划；
- **预测缺口 29 → 26**（`Number` 不在清单里），**以实测为准**。

## 状态

```
完整套件   1463 通过 / 0 失败 / 2 跳过（R312）
缺口       29（real = ceiling = 账本标题）
Commit     42.0 GB / 可用 5.98 GB   ← 远低于硬线，建议重启后再落地
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
