import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 317 轮：行家族 4 件落地 —— 缺口 **26 → 19**，又一次预测命中

### 一、按设计稿实现

```
src/Cybersole.Ui/Views/SmartActions/SmartActionRows.cs   FilterRow / FilterInputEntry / ActionRow / InputRow
tests/Cybersole.Tests/SmartActionRowTests.cs             6 条（对应设计稿的 6 条验收）
```

关键决定照旧执行：

- **`Passed` 由调用方传入**（`new FilterRow(f, passed: false, isFirst: index == 0)`）——
  行不持 `CheckoutEvent`，测试不需要跑结账；
- **`InputRow` 不接页面**（无证据），进入"声明但未构造"基线（+1）。

### 二、接进真实用处

`SmartActionsCreator.FilterRows` / `ActionRows` —— `IsFirst` 由位置决定，`Result`/`Tooltip` 默认空。

### 三、账本

```
bind_diff：missing 31 → real gap **19**（设计稿预测 19，实测 19）
ceiling 19；账本标题「当前 19 = 0 可做 + 19 结构」
```

### 四、连带计数（两处，都按规矩更新）

- `UnreachedUiTypesTests`：UI 类 **103**、不可达 **31**（`InputRow` 入基线；`FilterRow`/`ActionRow` 因被属性构造而不入）；
- `SummaryBlockTests`：指南 **103 / 31**。

### 五、验证

```
SmartActionRowTests + 计数守卫 + 绑定棘轮   22 + 5 通过 / 0 失败
```

全套未跑（内存一度到 4.1 GB，`build-server shutdown` 后回到 5.4 GB）。

### 六、这一轮的一句话

> 第三件、第四次"设计稿预测 → 实测命中"（29→26、26→19）。这已经不是运气：
> **把"我确定的"和"我不确定的"分开写，预测就能当尺子用。**

> 同时这轮也证明 `build-server shutdown` 是真有用的 —— 4.1 GB 回到 5.4 GB，救回了后半程。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 317 轮（行家族 4 件落地，缺口 **26 → 19**；UI 类 103 / 不可达 31）。

---

## B 类：7 件已完成，剩 2 件

| 已完成 | 轮次 | 关掉的成员 |
|---|---|---|
| `ComboBoxEdit` 族 | R312 | `ClearSelectionCommand`, `RemoveTokenCommand` |
| `ProfileCsvRow` | R314 | `FullySelected`, `RowError`, `RowStatus` |
| `FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` | R317 | `IsFirst`×3, `Passed`, `ValueText`, `Tooltip`, `Matched` |

**剩余 2 件**：`ElementCell.ColumnSpan`、`IWebhook.ExtraFields`（都在 `docs/B_CLASS_DECISIONS.md`）。
其余 19 条缺口是"已有等价物/不可得/内部状态"，不再动。

## 状态

```
完整套件   1468 通过（R315；R317 后未跑全套）
缺口       19（real = ceiling = 账本标题）
UI 类      103 声明 / 31 不可达
Commit     42.9 GB / 可用 5.4 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
