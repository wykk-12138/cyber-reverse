import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 314 轮：`ProfileCsvRow` 落地 —— 缺口 **29 → 26**，与设计稿预测一致

### 一、照设计稿做的

```
src/Cybersole.Ui/Views/Profiles/Modals/ProfileCsvRow.cs   （Number / FullySelected / RowStatus / RowError）
tests/Cybersole.Tests/ProfileCsvRowTests.cs               （5 条，全过）
```

判定规则与设计稿一致（可测、可解释）：

| 情况 | `RowError` | `RowStatus` |
|---|---|---|
| 全列非空 | 空 | `Ready (N columns)` |
| 缺列 | `Missing <列名>` | `M of N columns mapped` |
| 空行 | `Row is empty` | `Empty` |
| 下标越界 | 计入缺失 | 同上 |

### 二、接进了真实用处

`ProfileCsvEditorView.Rows`：把粘贴的 CSV 变成带状态的行列表。
**`ProfileCount` 回答"几条"，`Rows` 回答"哪一行有问题"** —— 后者才是原版 `RowError` 的用途。

接进去还有个副作用（好的那种）：`ProfileCsvRow` 现在**在 src 里被构造**，
所以它不会变成"声明了没人构造"的新基线项 —— 上一轮 `ComboBoxEdit` 需要加 baseline，这一件不需要。

### 三、账本

```
bind_diff：missing 38 → real gap **26**（设计稿预测 26，实测 26）
ceiling 26；账本标题「当前 26 = 0 可做 + 26 结构（A 类清零；R312 ComboBoxEdit、R314 ProfileCsvRow）」
```

### 四、验证

```
ProfileCsvRowTests + 绑定棘轮 + CSV 解析   11 通过 / 0 失败
```

**全套未跑**：可用内存已到 5.9 GB，按纪律不再拉起 26 秒的全套。

### 五、这一轮的一句话

> 这是第二次"设计稿预测 → 落地实测"完全对齐（29→26 对 29→26）。

> **因为这次预测里我特意把"我不确定的那一项"（`Number` 不在清单）标了出来 ——
> 预测写得诚实，实测才对得上。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 314 轮（`ProfileCsvRow` 落地，缺口 **29 → 26**；`ProfileCsvEditorView.Rows` 接上真实用处）。

---

## B 类第 2 件完成

```
src/Cybersole.Ui/Views/Profiles/Modals/ProfileCsvRow.cs   Number / FullySelected / RowStatus / RowError
src/Cybersole.Ui/Views/Profiles/ProfileViews.cs           ProfileCsvEditorView.Rows（真实用处）
tests/Cybersole.Tests/ProfileCsvRowTests.cs               5 条
```

- `ProfileCount` 回答"几条"，`Rows` 回答"哪一行有问题"；
- 因为被 src 构造，**不需要**加"未构造"基线（与 R312 的 `ComboBoxEdit` 相反）；
- 缺口 **29 → 26**（预测 26，实测 26）。

## 剩余 B 类待抽 6 件

`FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` / `ElementCell` / `IWebhook.ExtraFields`
（依据见 `docs/B_CLASS_DECISIONS.md`）。下件建议 `FilterRow`（3 成员，`IsFirst`/`Passed`/`ValueText`）。

## 状态

```
完整套件   1463 通过（R312；R314 后**未跑全套**，内存 5.9 GB）
缺口       26（real = ceiling = 账本标题）
mutation   29 条 / 锚点 29/29
Commit     42.1 GB / 可用 5.87 GB   ← 低于硬线，重启后再跑全套 + 下一件
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
