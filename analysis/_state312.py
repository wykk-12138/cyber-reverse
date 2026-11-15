import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 312 轮：`ComboBoxEdit` 落地 —— 缺口 **31 → 29**（B 类第一件）

### 一、照设计稿做的（`docs/CONTROL_DESIGN_ComboBoxEdit.md`）

新增 `src/Cybersole.Ui/Views/Controls/ComboBoxEdit.cs`：

| 原版绑定 | 实现 |
|---|---|
| `ComboBoxEdit.RemoveTokenCommand` | `RemoveToken(string)` + **同名命令别名**（`RelayCommand`） |
| `ComboBoxEdit.ClearSelectionCommand` | `ClearSelection()` + **同名命令别名** |
| `ComboBoxToken.Text` | `ComboBoxToken` 记录 |
| `ComboBoxGroupHeader.Name` | `ComboBoxGroupHeader` 记录 + 分组渲染 |

按设计稿：**多选 + token 可逐个移除 + 分组标题 + 一键清空**，且**不接到任何页面**（无页面证据）。

### 二、5 条测试，全过

`ComboBoxEditTests`：移除并触发一次 `Changed` / 清空返回计数且幂等 / 分组标题顺序 / 空选项不崩 / 重复文本只移除第一个。

### 三、账本

```
bind_diff：missing 41（原 43）→ real gap **29**（原 31）
ceiling 29，账本标题「当前 29 = 0 可做 + 29 结构（A 类清零；R312 关掉 ComboBoxEdit 两条）」
```

### 四、连带三处计数守卫（都按规矩更新，不是绕过）

新增 UI 类会让三条计数守卫变红：

- `UnreachedUiTypesTests`：`ComboBoxEdit` **故意不可达**（无页面证据），加入 baseline；
- `SummaryBlockTests`：指南 UI 类 97 → **98**、不可达 29 → **30**；
- `ParityDocTests`：`PARITY.md` 83 → **84**（26 Window + 57 → 58 UserControl）。

### 五、验证

```
ComboBoxEditTests            5 通过
绑定棘轮 + 死字段守卫          10 通过
完整套件                     1463 通过 / 0 失败 / 2 跳过（26 s）
```

### 六、这一轮的一句话

> 设计稿里写的"完成后 31 → 29"，**落地后实测就是 29** —— 这是少数几次预测与实测一致的轮次。

> 而"故意不可达"这件事必须先写进 baseline 再谈通过：**否则守卫会把我的新控件当成又一个死视图。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 312 轮（`ComboBoxEdit` 落地，缺口 **31 → 29**；UI 类 98 / 不可达 30）。

---

## B 类第 1 件完成：`ComboBoxEdit`

```
src/Cybersole.Ui/Views/Controls/ComboBoxEdit.cs   （多选 + token + 分组 + 清空）
tests/Cybersole.Tests/ComboBoxEditTests.cs        （5 条，全过）
```

- `RemoveTokenCommand` / `ClearSelectionCommand` 以**同名命令别名**存在（`RelayCommand`），与 `NotificationOptions.EnableSound` 同一手法；
- **故意不接页面**（无页面证据，遵循 R265）；已加入 `UnreachedUiTypesTests` 的 baseline；
- 计数同步：指南 UI 类 **98** / 不可达 **30**；`PARITY.md` **84**（26 Window + 58 UserControl）。

## 缺口 29 的构成（B 类待抽的还剩 7 件）

`ProfileCsvRow` / `FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` / `ElementCell` / `IWebhook.ExtraFields`
（各附依据见 `docs/B_CLASS_DECISIONS.md`）。下一件建议 `ProfileCsvRow`（4 成员，行控件）。

## 状态

```
完整套件   1463 通过 / 0 失败 / 2 跳过（R312）
mutation   29 条 / 锚点 29/29（R307 后未再全量）
缺口       29（real = ceiling = 账本标题）
Commit     41.5 GB / 可用 6.25 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
